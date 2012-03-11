"""Python API for the Microsoft TerraServer.
Copyright (c) 2012 Howard Butler hobu@hobu.net

License:
See the Python 2.6 License (http://www.python.org/2.6/license.html)
"""

import datetime

wsdl = 'http://msrmaps.com/TerraService2.asmx?WSDL'

from suds.client import Client

client = Client(wsdl)

import logging
logging.basicConfig(level=logging.INFO)
# logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.getLogger('suds.client').setLevel(logging.ERROR)

themes = {'DOQ':1, 'DRG':2, "ORTHO":1, "TOPO":2}

__author__ = "Howard Butler  hobu@hobu.net"
__copyright__ ='(c) 2012 Howard Butler'

url = "http://msrmaps.com/TerraService2.asmx"
ns = "http://msrmaps.com/"


class pyTerraError(Exception):
    """Custom exception for PyTerra"""

    
def GetPlaceList(placeName, MaxItems=10, imagePresence=True):
    """Returns a list of PlaceItems that have the same placeName"""
    try:
        resp = client.service.GetPlaceList(placeName, int(MaxItems), str(bool(imagePresence)).lower())
    except Exception, e:
        raise pyTerraError(e)

    return resp

def GetPlaceTypes():
    t = client.factory.create("PlaceType")
    return [i[0] for i in t]

def GetScales():
    t = client.factory.create("Scale")
    return [i[0] for i in t]

def GetPlaceListInRect(upperLeft, lowerRight, ptype, MaxItems):
    """Returns a list of places inside the bounding box"""
    #This function is not known to return good results

    ul = client.factory.create("LonLatPt")
    ul.Lat = float(upperLeft.Lat)
    ul.Lon = float(upperLeft.Lon)

    lr = client.factory.create("LonLatPt")
    lr.Lat = float(lowerRight.Lat)
    lr.Lon = float(lowerRight.Lon)

    if (ptype not in GetPlaceTypes()):
        raise pyTerraError("type %s not available" % ptype)
    try:
        resp = client.service.GetPlaceListInRect(ul, lr, ptype, MaxItems)
    except Exception, e:
        raise pyTerraError(e)

    return resp


def GetPlaceFacts(place):
    """Gets facts about a place (park, CityTown, etc..)"""

    p = client.factory.create("Place")
    p.City = place.City
    p.State = place.State
    p.Country = place.Country
    
    try:
        resp = client.service.GetPlaceFacts(p)
    except Exception, e:
        raise pyTerraError(e)

    return resp

    
def GetAreaFromPt(center, theme, scale, displayPixWidth, displayPixHeight):
    """Returns an area (set of tiles) defined by a point"""
    
    p = client.factory.create("LonLatPt")
    p.Lat = float(center.Lat)
    p.Lon = float(center.Lon)
    
    displayPixHeight = int(displayPixHeight)
    displayPixWidth = int(displayPixHeight)
    
    if (scale not in GetScales()):
        raise pyTerraError("Scale '%s' is not a valid scale" % scale)

    try:
        int(theme)
    except ValueError:
        try:
            theme = themes[theme.upper()]
        except KeyError:
            raise pyTerraError("Theme %s not found" % theme)


    try:
        resp = client.service.GetAreaFromPt(p, theme, scale, displayPixWidth, displayPixHeight)
    except Exception, e:
        raise pyTerraError(e)

    return resp
    

def GetAreaFromTileId(id, displayPixWidth=200, displayPixHeight=200):
    """Returns the bounding box for a TileMeta.Id"""

    t = client.factory.create("TileId")
    t.X = int(id.X)
    t.Y = int(id.Y)
    t.Scene = int(id.Scene)
    t.Theme = id.Theme
    t.Scale = id.Scale
    
    displayPixHeight = int(displayPixHeight)
    displayPixWidth = int(displayPixHeight)
    
    if (t.Scale not in GetScales()):
        raise pyTerraError("Scale '%s' is not a valid scale" % t.Scale)

    try:
        int(id.Theme)
    except ValueError:
        try:
            t.Theme = themes[id.Theme.upper()]
        except KeyError:
            raise pyTerraError("Theme %s not found" % id.Theme)

    try:
        resp = client.service.GetAreaFromTileId(t, displayPixWidth, displayPixHeight)
    except Exception, e:
        raise pyTerraError(e)

    return resp
            


def GetAreaFromRect(upperLeft, lowerRight, theme, scale):
    """Returns the tiles for the bounding box defined two points, upperLeft and lowerRight.
    
    :param upperLeft: an instance with .Lat and .Lon data members 
        The .Lat and .Lon data members of the instance passed in represent the 
        WGS84 latitude and longitude, and should be provided as floating point nubmers.

    :param lowerRight: an instance with .Lat and .Lon data members 
        The .Lat and .Lon data members of the instance passed in represent the 
        WGS84 latitude and longitude, and should be provided as floating point nubmers.

    :param theme: integer
        An integer from one of the valid themes in :data:`themes`.

    :param scale: string
        A valid scale string from :meth:GetScales
    """

    ul = client.factory.create("LonLatPt")
    ul.Lat = float(upperLeft.Lat)
    ul.Lon = float(upperLeft.Lon)

    lr = client.factory.create("LonLatPt")
    lr.Lat = float(lowerRight.Lat)
    lr.Lon = float(lowerRight.Lon)

    try:
        int(theme)
    except ValueError:
        try:
            theme = themes[theme.upper()]
        except KeyError:
            raise pyTerraError("Theme %s not found" % theme)
    if (scale not in GetScales()):
        raise pyTerraError("scale %s not available" % scale)
    try:
        resp = client.service.GetAreaFromRect(ul, lr, theme, scale)
    except Exception, e:
        raise pyTerraError(e)

    return resp

    
def GetTileMetaFromTileId(id):
    """Gets the metadata for a TileMeta.Id"""

    t = client.factory.create("TileId")
    t.X = int(id.X)
    t.Y = int(id.Y)
    t.Scene = int(id.Scene)
    t.Theme = id.Theme
    t.Scale = id.Scale
    
    if (t.Scale not in GetScales()):
        raise pyTerraError("Scale '%s' is not a valid scale" % t.Scale)

    try:
        int(id.Theme)
    except ValueError:
        try:
            t.Theme = themes[id.Theme.upper()]
        except KeyError:
            raise pyTerraError("Theme %s not found" % id.Theme)

    try:
        resp = client.service.GetTileMetaFromTileId(t)
    except Exception, e:
        raise pyTerraError(e)

    return resp    


def GetTileMetaFromLonLatPt(point, theme, scale):
    """Gets the TileMeta for a point (lat/lon)"""

    p = client.factory.create("LonLatPt")
    p.Lat = float(point.Lat)
    p.Lon = float(point.Lon)

    try:
        int(theme)
    except ValueError:
        try:
            theme = themes[theme.upper()]
        except KeyError:
            raise pyTerraError("Theme %s not found" % theme)

    try:
        resp = client.service.GetTileMetaFromLonLatPt(p, theme, scale)
    except Exception, e:
        raise pyTerraError(e)

    return resp


def GetTile(id):
    """Returns the tile image data"""

    t = client.factory.create("TileId")
    t.X = int(id.X)
    t.Y = int(id.Y)
    t.Scene = int(id.Scene)
    t.Theme = id.Theme
    t.Scale = id.Scale
    
    if (t.Scale not in GetScales()):
        raise pyTerraError("Scale '%s' is not a valid scale" % t.Scale)

    try:
        int(id.Theme)
    except ValueError:
        try:
            t.Theme = themes[id.Theme.upper()]
        except KeyError:
            raise pyTerraError("Theme %s not found" % id.Theme)
            
    try:
        resp = client.service.GetTile(t)
    except Exception, e:
        raise pyTerraError(e)

    return resp
def ConvertLonLatPtToNearestPlace(point):
    """Converts a lat/lon point into a place"""

    p = client.factory.create("LonLatPt")
    p.Lat = float(point.Lat)
    p.Lon = float(point.Lon)

    try:
        resp = client.service.ConvertLonLatPtToNearestPlace(p)
    except Exception, e:
        raise pyTerraError(e)

    return resp


def ConvertUtmPtToLonLatPt(utm):
    """Converts a UTM point into lat/lon"""

    p = client.factory.create("UtmPt")
    p.X = float(utm.X)
    p.Y = float(utm.Y)
    p.Zone = int(utm.Zone)

    try:
        resp = client.service.ConvertUtmPtToLonLatPt(p)
    except Exception, e:
        raise pyTerraError(e)

    return resp


def ConvertLonLatPtToUtmPt(point):
    """Converts a lat/lon point into UTM"""

    p = client.factory.create("LonLatPt")
    p.Lat = float(point.Lat)
    p.Lon = float(point.Lon)

    try:
        resp = client.service.ConvertLonLatPtToUtmPt(p)
    except Exception, e:
        raise pyTerraError(e)

    return resp


def ConvertPlaceToLonLatPt(place):
    """Converts a place struct into a lat/lon point"""
    p = client.factory.create("Place")
    p.City = place.City
    p.State = place.State
    p.Country = place.Country
    
    try:
        resp = client.service.ConvertPlaceToLonLatPt(p)
    except Exception, e:
        raise pyTerraError(e)

    return resp

def GetTheme(theme):
    """Returns theme information about a theme (Photo, Topo, or Relief)"""

    try:
        int(theme)
    except ValueError:
        try:
            theme = themes[theme.upper()]
        except KeyError:
            raise pyTerraError("Theme %s not found" % theme)

    try:
        resp = client.service.GetTheme(theme=theme)
    except Exception, e:
        raise pyTerraError(e)

    return resp


def CountPlacesInRect(upperLeft, lowerRight, ptype):
    """Counts the number of places inside the bounding box with the specified ptype"""

    ul = client.factory.create("LonLatPt")
    ul.Lat = float(upperLeft.Lat)
    ul.Lon = float(upperLeft.Lon)

    lr = client.factory.create("LonLatPt")
    lr.Lat = float(lowerRight.Lat)
    lr.Lon = float(lowerRight.Lon)

    if (ptype not in GetPlaceTypes()):
        raise pyTerraError("type %s not available" % ptype)    

    try:
        resp = client.service.CountPlacesInRect(ul, lr, ptype)
    except Exception, e:
        raise pyTerraError(e)

    return resp


def GetLatLonMetrics(point):
    """Don't know why this is there or what this does"""

    p = client.factory.create("LonLatPt")
    p.Lat = float(point.Lat)
    p.Lon = float(point.Lon)

    try:
        resp = client.service.GetLatLonMetrics(p)
    except Exception, e:
        raise pyTerraError(e)

    return resp
