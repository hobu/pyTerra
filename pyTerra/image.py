try:
    import pyTS.pyTerra as pyTerra
    import pyTS.SOAPpy
    from pyTS.SOAPpy import Types
except ImportError:
    import sys
    sys.path.append('..')
    import pyTerra
    from SOAPpy import Types
    
from threading import Thread
import Queue
import os
import sys
import Image
import cStringIO
import base64
import time
pyTerra.retries = 6
#Number of pixels on a side of a tile
side = 200

class Retriever(Thread):
    """Retrives tiles as part of a simple thread pool so that
    trying to fetch 100 tiles doesn't create 100 threads"""
    def __init__(self, tileq):
        Thread.__init__(self)
        self.setDaemon(1)  # so we can kill the script easily
        self.tileq = tileq
    def run(self):
        while True:
            tile = self.tileq.get()
            if tile is None:
                break
            
            try:
                tile.imagedata = base64.decodestring(pyTerra.GetTile(tile))
            except:
                #sleep the thread for a second and try once more
                time.sleep(1)
                tile.imagedata = base64.decodestring(pyTerra.GetTile(tile))

class point(Types.structType):
    def __init__(self, Lat, Lon):
        Types.structType.__init__(self, None, (pyTerra.ns,'point'), 1, None)
       # self._aslist    = []
       # self._asdict    = {}
       # self._keyord    = []
        self._addItem('Lat', float(Lat))
        self._addItem('Lon', float(Lon))

class utm(Types.structType):
    def __init__(self, X, Y, Zone):
        Types.structType.__init__(self, None, (pyTerra.ns,'utm'), 1, None)
       # self._aslist    = []
       # self._asdict    = {}
       # self._keyord    = []
        self._addItem('X', float(X))
        self._addItem('Y', float(Y))
        self._addItem('Zone', int(Zone))
        
class TerraImage(object):
    def __init__(self, upperLeft, lowerRight, Scale, Theme, Zone, cacheDir=None):
        if not (Theme.upper() <> 'PHOTO' or Theme.upper() <> 'TOPO'):
            raise pyTerra.pyTerraError('Theme must be Photo or Topo, not %s' % Theme)
        if Scale[:5] <> 'Scale' or Scale[-1:] <> 'm':
            raise pyTerra.pyTerraError('Scale must be in the form Scale2m, Scale4m, etc., not %s' % Scale)
        try:
            int(Zone)
            if not 10 <= int(Zone) <= 19:
                raise pyTerra.pyTerraError('Zone must be between 10 and 19')
        except ValueError:
            raise pyTerra.pyTerraError('Zone must be an integer between 10 and 19')
        if not (isinstance(upperLeft, utm) or isinstance(upperLeft, point)):
            raise pyTerra.pyTerraError('upperLeft must be an instance of pyTerra.point or pyTerra.utm')
        if not (isinstance(lowerRight, utm) or isinstance(lowerRight, point)):
            raise pyTerra.pyTerraError('upperLeft must be an instance of pyTerra.point or pyTerra.utm')
        self.upperLeft = upperLeft
        self.lowerRight = lowerRight
        self.Scale = Scale
        self.Theme = Theme
        self.Zone = Zone
        self.retrieverThreads = 5  # max number threads in retriever pool
        self.cacheDir = None
        if cacheDir and os.path.isdir(cacheDir):
            # use this directory to cache tiles locally
            self.cacheDir = cacheDir

    def _get_extent(self):
        if isinstance(self.upperLeft, utm):
            uL = pyTerra.ConvertUtmPtToLonLatPt(self.upperLeft)
            self.upperLeft = point(uL.Lat, uL.Lon)
        if isinstance(self.lowerRight, utm):
            lR = pyTerra.ConvertUtmPtToLonLatPt(self.lowerRight)
            self.lowerRight = point(lR.Lat, lR.Lon)
        self.extent = pyTerra.GetAreaFromRect(self.upperLeft, self.lowerRight,
                                              self.Theme, self.Scale)
        nw, ne = self.extent.NorthWest, self.extent.NorthEast
        sw, se = self.extent.SouthWest, self.extent.SouthEast
        startx = int(nw.TileMeta.Id.X)
        # TerraServer has a weird bug where sometimes the sw.Y will
        # be one lower than the se.Y.  Until it is fixed, use se
        starty = int(se.TileMeta.Id.Y)
        self.numx = int(ne.TileMeta.Id.X) - int(nw.TileMeta.Id.X) + 1
        self.numy = int(nw.TileMeta.Id.Y) - int(se.TileMeta.Id.Y) + 1
        self.width = self.numx * side
        self.height = self.numy * side
        tileslist = []
        for x in range(int(nw.TileMeta.Id.X), int(nw.TileMeta.Id.X) + self.numx):
            for y in range(int(se.TileMeta.Id.Y), int(se.TileMeta.Id.Y) + self.numy):
                t = Types.structType(name=(pyTerra.ns,'ns1'))
                t._addItem('Scene', self.Zone) #t.Scene = float(X))Scene = self.Zone
                t._addItem('X', int(x)); t._addItem('Y', int(y))
                t._addItem('Scale', self.Scale); t._addItem('Theme', self.Theme) 
                t.xind = (x - startx)
                t.yind = -1*(y - starty)+(self.numy - 1) #order of tiles is opposite in PIL
                tileslist.append(t)
        self.tileslist = tileslist
        return self.tileslist

    def _get_cache_filename(self, tile):
        """Return the cache filename for this tile"""
        tid = '%s-%s-%s-%s-%s.gif' % (tile.Theme, tile.Scene, tile.X, tile.Y,
                                     tile.Scale)
        cachefile = os.path.join(self.cacheDir, tid)
        return cachefile
    
    def _retrieve_from_cache(self, tile):
        """Fetch the tile from cache if it exists.  Return 0 if the
        tile isn't in the cache"""
        if not self.cacheDir: return 0
        cachefile = self._get_cache_filename(tile)
        if os.path.isfile(cachefile):
            f = open(cachefile, "rb")
            tile.imagedata = f.read()
            f.close()
            return 1
        return 0

    def _add_to_cache(self, tile):
        """Save this tile to the cache"""
        if not self.cacheDir: return
        cachefile = self._get_cache_filename(tile)
        f = open(cachefile, "wb")
        f.write(tile.imagedata)
        f.close()
    
    def _get_tile_data(self):
        threadList = []
        tileQueue = Queue.Queue()
        # Set up the thread pool.  All the threads will read tiles from the
        # tileQueue until they read a None
        for i in range(self.retrieverThreads):
            retriever = Retriever(tileQueue)
            retriever.start()
            threadList.append(retriever)

        toCacheList = []
        for tile in self.tileslist:
            if not self._retrieve_from_cache(tile):
                # this tile needs to be downloaded
                tileQueue.put(tile)
                toCacheList.append(tile)

        # Shut down the thread pool. And wait for them to finish.
        for i in range(self.retrieverThreads):
            tileQueue.put(None)
        for retriever in threadList:
            retriever.join()

        # Add any newly fetched tiles to the cache
        for tile in toCacheList:
            self._add_to_cache(tile)

        n = Image.new("RGB", (self.width, self.height))
        for tile in self.tileslist:
            i = Image.open(cStringIO.StringIO(tile.imagedata))
            topx = tile.xind * side
            topy = tile.yind * side
            bottomx = (tile.xind * side) + side
            bottomy = (tile.yind * side) + side
            thebox = (topx,topy,bottomx,bottomy)
            n.paste(i,thebox)
        self.image = n
        return n

    def download(self):
        """Do the download and create the image, return the PIL Image"""
        try:
            self.extent
            self.tileslist
        except AttributeError:
            self._get_extent()
        try:
            self.image
        except AttributeError:
            self._get_tile_data()
        return self.image
        
    def write(self, filename):
        """Do the download, create the image and save it to disk"""
        dir, fname = os.path.split(filename)
        root, ext = os.path.splitext(fname)
        if (ext=='.tif' or ext=='.tiff'):
            format="TIFF"
        elif (ext=='.jpg' or ext=='.jpeg'):
            format='JPEG'
        else:
            raise ValueError("Unsupported extention %s" % ext)

        self.download()

        afile = open(filename, 'wb')
        self.image.save(afile, format=format)
        afile.close()
        return 1

    def _get_worldfile(self):
        """Returns the worldfile for the TerraImage instance"""
        try:
            self.extent
        except AttributeError:
            self._get_extent()
        id = self.extent.NorthWest.TileMeta.Id
        nwcorner = pyTerra.GetTileMetaFromTileId(id).NorthWest
        nwcorner = pyTerra.ConvertLonLatPtToUtmPt(nwcorner)
        scale = self.Scale.replace('Scale','')
        scale = scale.replace('m','')
        self.worldfile=scale+"\n"+"0.0\n0.0\n-"+scale+"\n"+str(nwcorner.X)+"\n"+str(nwcorner.Y)
        return self.worldfile

    def write_worldfile(self, filename):
        """Writes the worldfile for the TerraImage instance to the filename location specified"""
        try:
            self.worldfile
        except AttributeError:
            self._get_worldfile()
        filename=filename
        afile = open(filename,'w')
        afile.write(self.worldfile)
        afile.close()
        
    def _get_number_of_tiles(self):
        """Returns the number of tiles for the TerraImage instance"""
        try:
            return self.numx*self.numy
        except AttributeError:
            self._get_extent()
            return self.numx*self.numy
    number_of_tiles = property(_get_number_of_tiles)

    def _unique(self, alist):
        u = {}
        try:
            for x in alist:
                u[x] = 1
        except TypeError:
            del u  # move on to the next method
        else:
            return u.keys()
        
    def _get_dates(self):
        """Gets the range of dates for each tile in the TerraImage.  Could be slow as it is making a request for each tile"""
        #Set the scale to 16 m or greater.  That way we won't have as many tiles to check
        orig_scale = int(self.Scale[5:][:-1])
        if orig_scale < 16:
            self.Scale = 'Scale16m'
        self._get_extent()
        dates = []
        for tile in self.tileslist:
            date = pyTerra.GetTileMetaFromTileId(tile).Capture[:10]
            dates.append(date)
        dates = self._unique(dates)
        #Set the scale back to its original value
        self.Scale = 'Scale%sm' % orig_scale
        return dates
    dates = property(_get_dates)



    
if __name__ =='__main__':
    try:
        large = sys.argv[1]
    except:
        large = 0
    if large:
        ul_x = 433714.25
        ul_y = 4661043.80
        lr_x = 438603.35
        lr_y = 4656591.96
    else:
    #Baker field
        ul_x = 436521.25
        ul_y = 4659253.80
        lr_x = 437142.35
        lr_y = 4658582.96
    thescale = 'Scale1m'
    thetype = 'Photo'
    thezone = 15
    filename = 'test.jpg'
    
    p = point(43.003, 93.00)
    upperLeft = utm(ul_x, ul_y, thezone)
    lowerRight = utm(lr_x, lr_y, thezone)
    ti = TerraImage(upperLeft, lowerRight, thescale, thetype, thezone)
    print ti.number_of_tiles

    ti.write_worldfile('test.jpgw')
    ti.write('test.jpg')
    ti.write_worldfile('test.jpgw')
#    print ti.dates
