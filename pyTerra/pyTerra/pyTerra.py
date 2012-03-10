"""Python API for the Microsoft TerraServer.
Copyright (c) 2012 Howard Butler hobu@hobu.net

*******************************************************************************
pyTerra: Python Support for the Microsoft TerraServer

*******************************************************************************
Version: 0.9

*******************************************************************************
License:
See the Python 2.6 License (http://www.python.org/2.6/license.html)

*******************************************************************************
Description:
pyTerra is a Python module that allows you to make requests to Microsoft's
TerraServer (http://terraserver.microsoft.com/).  With it, you can download
cartographic images for any almost any geographic extent in the US.

The TerraServer has almost complete coverage of the United States for two very
important cartographic products, topographic maps and digital orthographic
photos (sometimes called DOQs or DOQQs).  You can find out more about DOQs here
(http://mapping.usgs.gov/www/ndop/) and more about what topographic maps are
here  (http://mac.usgs.gov/mac/isb/pubs/booklets/symbols/).

All methods reflect the TerraService API.  See the WSDL file at
http://terraserver-usa.com/terraservice.asmx for more information about how
to make the calls.  Every call returns SOAPpy objects (which are very similar
to regular objects).  You can traverse the heirarchy by taking a response
and going obj.obj.obj...  

This software requires a hacked version of SOAPpy 0.10.1 because TerraServer
is very picky about how it receives namespaces.  I couldn't find any other
way around it other than to hack in what it expected into the SOAPBuilder of
SOAPpy.  The hacked version of SOAPpy is included in the module.

The TerraServer stores images as a pyramid of tiles.  Each tile is always 200
pixels square, independent of its actual ground resolution.  Aerial photos are
available in 1, 2, 4, 8, 16, 32, and 64 m resolutions.  Topographic maps are
available in all of the above resolutions except 1-meter.

Getting an image for an extent involves three steps: 1. Define a bounding box
for the area you want to download. A bounding box is a box defined by the upper
left point and lower left point of the box.  The point can be in geographic
coordinates (42.9332 deg N x -93.2112 deg W) or projected UTM coordinates
(437679.183 Easting and 4658340.891 Northing) 2. Make a request to the
Terraserver that returns all of the tiles that fall within the bounding box 3.
Make a request to the Terraserver for the image data in each tile and paste it
into a new PIL image.

*******************************************************************************

Requires:
Python 2.2 or greater

pyXML 0.8.2 or greater
(http://sourceforge.net/project/showfiles.php?group_id=6473)

*******************************************************************************
Future plans:
This version of pyTerra removes the need for the Microsoft SOAP kit that the
previous version required.  This means that 0.4 is now a Python-only version
of the software and should work in Unix environments as well as Windows.  

*******************************************************************************

*******************************************************************************
Testing:
A series of unit tests has been written for this version.  To start the tests,
run pyTerra -v at a command prompt.  The tests check the software to make
sure that it is returning correct results and errors.  The area that it uses
to check its information is in Iowa.

*******************************************************************************
"""

import datetime

wsdl = 'http://msrmaps.com/TerraService2.asmx?WSDL'

from suds.client import Client
client = Client(wsdl)

import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)

lookup = {'DOQ':1, 'DRG':2, "ORTHO":1}

__author__ = "Howard Butler  hobu@hobu.net"
__copyright__ ='(c) 2012 Howard Butler'

url = "http://msrmaps.com/TerraService2.asmx"
ns = "http://msrmaps.com/"
debug = 1

retries = 2

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
            theme = lookup[theme.upper()]
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
            t.Theme = lookup[id.Theme.upper()]
        except KeyError:
            raise pyTerraError("Theme %s not found" % id.Theme)

    try:
        resp = client.service.GetAreaFromTileId(t, displayPixWidth, displayPixHeight)
    except Exception, e:
        raise pyTerraError(e)

    return resp
            


def GetAreaFromRect(upperLeft, lowerRight, theme, scale):
    """Returns the tiles for the bounding box defined by upperLeft and lowerRight"""

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
            theme = lookup[theme.upper()]
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
            t.Theme = lookup[id.Theme.upper()]
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
            theme = lookup[theme.upper()]
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
            t.Theme = lookup[id.Theme.upper()]
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
            theme = lookup[theme.upper()]
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

class Object:
    pass
    
    
if __name__ == '__main__':
    
    import unittest
    import sys
    imagePresence='true'
    MaxItems='10'
    placeName='Ames'
    theme = 1
    scale = "Scale4m"
    ptype = 'CityTown'
    
    displayPixWidth = 200
    displayPixHeight = 200
    
    place = Object()
    place.City = 'Ames'
    place.State = 'Iowa'
    place.Country = 'United States'
    
    pt = Object()
    pt.Lon = -93.000
    
    pt.Lat = 43.000
    center = pt

    upperLeft = Object()
    upperLeft.Lon = -93.000
    upperLeft.Lat = 43.000
    
    lowerRight = Object()
    lowerRight.Lon = -92.8999
    lowerRight.Lat = 42.8999
    
    class PyTerraTest(unittest.TestCase):
        def testGetAreaFromPtassert(self):
            """GetAreaFromPt traps bad inputs"""
            self.assertRaises(pyTerraError,
                              GetAreaFromPt,
                              center, theme, 'Scale4', displayPixWidth, displayPixHeight)
            self.assertRaises(pyTerraError,
                              GetAreaFromPt,
                              center, 'Photos', scale, displayPixWidth, displayPixHeight)
        def testGetAreaFromPtequals(self):
            """GetAreaFromPt returns correct results"""
            resp = GetAreaFromPt(center, theme, scale, displayPixWidth, displayPixHeight)
            id = resp.NorthWest.TileMeta.Id
            expected_x = 624
            expected_y = 5951
            expected_date = '1994-04-23'
            self.assertEqual(id.Y, expected_y)
            self.assertEqual(id.X, expected_x)
            self.assertEqual(resp.NorthWest.TileMeta.Capture, datetime.datetime(1994,4,23,0,0))

        def testGetPlaceListequals(self):
            """GetPlaceList returns Ames, Iowa as first result"""
            resp = GetPlaceList(placeName, MaxItems, imagePresence)
            ames = resp.PlaceFacts[0]
            self.assertEqual(ames.Place.State,"Iowa")
            self.assertEqual(ames.Place.City,"Ames")
        def testConvertLonLatPtToNearestPlaceassert(self):
            """ConvertLonLatPtToNearestPlace traps bad inputs"""
            pt.Lat = 'abc'
            self.assertRaises(ValueError,
                              ConvertLonLatPtToNearestPlace,
                              pt)
        def testConvertLonLatPtToNearestPlaceequals(self):
            """ConvertLonLatPtToNearestPlace returns 7 km SW of Rockford, Iowa"""
            pt.Lon = -93.000
            pt.Lat = 43.000
            resp = ConvertLonLatPtToNearestPlace(pt)
            expected_resp = '7 km SW of Rockford, Iowa, United States'
            self.assertEqual(resp, expected_resp)
        def testConvertLonLatPtToUtmPtequals(self):
            """ConvertLonLatPtToUtmPt returns correct results"""
            pt.Lon = -93.000
            pt.Lat = 43.000
            resp = ConvertLonLatPtToUtmPt(pt)
            expected_x = '500000.0000000000'
            expected_y = '4760814.7962907264'
            expected_zone = '15'
            self.assertEqual('%.10f' % resp.X, expected_x)
            self.assertEqual('%.10f' % resp.Y, expected_y)
            self.assertEqual('%d' % resp.Zone, expected_zone)
        def testConvertLonLatPtToUtmPtassert(self):
            """ConvertLonLatPtToUtmPt traps bad inputs"""
            pt.Lat = 'abc'
            self.assertRaises(ValueError,
                              ConvertLonLatPtToUtmPt,
                              pt)       
        def testGetTileMetaFromTileIdassert(self):
            """GetTileMetaFromTileId traps bad inputs"""
            id = Object()
            id.X = 'abc'
            id.Y = '5951'
            id.scene = '15'
            id.theme = theme
            id.scale = scale
            self.assertRaises(ValueError,
                              GetTileMetaFromTileId,
                              id)
        def testGetTileMetaFromTileIdtequals(self):
            """GetTileMetaFromTileId returns correct results"""
            resp = GetAreaFromPt(center, theme, scale, displayPixWidth, displayPixHeight)
            id = resp.NorthWest.TileMeta.Id
            resp = GetTileMetaFromTileId(id)
            self.assertEqual('%.10f' % resp.NorthWest.Lat, '43.0070686340')
            self.assertEqual('%.10f' % resp.NorthWest.Lon, '-93.0098190308')
        def testGetAreaFromTileIdassert(self):
            """GetAreaFromTileId traps bad inputs"""
            id = Object()
            id.X = 'abc'
            id.Y = '5951'
            id.scene = '15'
            id.theme = theme
            id.scale = scale
            self.assertRaises(ValueError,
                              GetAreaFromTileId,
                              id)
        def testGetAreaFromTileIdequals(self):
            """GetAreaFromTileId returns correct results"""
            id = Object()
            id.X = '624'
            id.Y = '5951'
            id.Scene = '15'
            id.Theme = theme
            id.Scale = scale
            resp = GetAreaFromTileId(id)
            self.assertEqual('%.10f' % resp.NorthWest.TileMeta.NorthWest.Lat, '43.0142745972')
            self.assertEqual('%.10f' % resp.NorthWest.TileMeta.NorthWest.Lon, '-93.0196380615')
        def testGetTileassert(self):
            """GetTile traps bad inputs"""
            id = Object()
            id.X = 'abc'
            id.Y = '5951'
            id.Scene = '15'
            id.Theme = theme
            id.Scale = scale
            self.assertRaises(ValueError,
                              GetTile,
                              id)
        def testGetTileequals(self):
            """GetTile returns correct results"""
            id = Object()
            id.X = '624'
            id.Y = '5951'
            id.Scene = '15'
            id.Theme = theme
            id.Scale = scale
            resp = GetTile(id)
            self.assertEqual(len(resp), 6852)

        def testConvertUtmPtToLonLatPtassert(self):
            """ConvertUtmPtToLonLatPt traps bad inputs"""
            utm = Object()
            utm.X = 'abc'
            utm.Y = '4760814.7962907264'
            utm.Zone = '15'
            self.assertRaises(ValueError,
                              ConvertUtmPtToLonLatPt,
                              utm)
        def testConvertUtmPtToLonLatPtequals(self):
            """ConvertUtmPtToLonLatPt returns correct results"""
            utm = Object()
            utm.X = '500000'
            utm.Y = '4760814.7962907264'
            utm.Zone = '15'
            resp = ConvertUtmPtToLonLatPt(utm)
            self.assertEqual('%.10f' % resp.Lat, '43.0000000000')
            self.assertEqual('%.10f' % resp.Lon, '-93.0000000000')
        def testGetAreaFromRectassert(self):
          """GetAreaFromRect traps bad inputs"""
          self.assertRaises(pyTerraError,
                            GetAreaFromRect,
                            upperLeft,
                            lowerRight,
                            theme,
                            'scale4')
        def testGetAreaFromRectequals(self):
            """GetAreaFromRect returns correct results"""
            resp = GetAreaFromRect(upperLeft,
                                   lowerRight,
                                   theme,
                                   scale)
            self.assertEqual('%.10f' % resp.NorthWest.TileMeta.NorthWest.Lat, '43.0070724487')
            self.assertEqual('%.10f' % resp.NorthWest.TileMeta.NorthWest.Lon, '-93.0000000000')


        def testGetLatLonMetricsassert(self):
            """GetLatLonMetrics traps bad inputs"""
            upperLeft.Lat = 'abc'
            self.assertRaises(ValueError,
                              GetLatLonMetrics,
                              upperLeft)
        def testGetLatLonMetricsassert(self):
            """GetLatLonMetrics returns correct results"""
            resp = GetLatLonMetrics(upperLeft)
        
        def testCountPlacesInRect(self):
            """Counting places in rect"""
            lowerRight = Object()
            lowerRight.Lon = -92.80
            lowerRight.Lat = 42.60
            resp = CountPlacesInRect(upperLeft, lowerRight, 'CityTown')
            self.assertEqual(resp, 15)
        def testGetPlaceListInRectEquals(self):
          """GetPlaceListInRect traps bad inputs"""
          lowerRight = Object()
          lowerRight.Lon = -92.80
          lowerRight.Lat = 42.60
          resp = GetPlaceListInRect(
                            upperLeft,
                            lowerRight,
                            'CityTown',
                            MaxItems)
          self.assertEqual(resp.PlaceFacts[0].Place.City, 'Greene');
        def testGetPlaceListInRectassert(self):
          """GetPlaceListInRect traps bad inputs"""
          self.assertRaises(pyTerraError,
                            GetPlaceListInRect,
                            upperLeft,
                            lowerRight,
                            'abc',
                            MaxItems)
        
        def testConvertPlaceToLonLatPtsequals(self):
            """GetPlaceFacts returns correct results"""
            place = Object()
            place.City = 'Ames'
            place.State = 'Iowa'
            place.Country = 'United States'
            resp = ConvertPlaceToLonLatPt(place)
            self.assertEqual('%.10f' % resp.Lat, '42.0299987793')
            self.assertEqual('%.10f' % resp.Lon, '-93.6100006104')
        
        def testGetPlaceFactsassert(self):
          """GetPlaceFacts traps bad inputs"""
          place.City = 43.200
          self.assertRaises(pyTerraError,
                            GetPlaceFacts,
                            place)
        def testGetPlaceFactsequals(self):
            """GetPlaceFacts returns correct results"""
            place = Object()
            place.City = 'Ames'
            place.State = 'Iowa'
            place.Country = 'United States'
            resp = GetPlaceFacts(place)
            self.assertEqual('%.10f' % resp.Center.Lat, '42.0299987793')
            self.assertEqual('%.10f' % resp.Center.Lon, '-93.6100006104')
        def testGetTileMetaFromLonLatPtassert(self):
          """GetTileMetaFromLonLatPt traps bad inputs"""
          self.assertRaises(pyTerraError,
                            GetTileMetaFromLonLatPt,
                            pt,
                            'Photos',
                            scale)
        def testGetTileMetaFromLonLatPtequals(self):
            """GetTileMetaFromLonLatPt returns correct results"""
            
            resp = GetTheme('ortho')
            resp = GetTileMetaFromLonLatPt(pt, theme, scale)
            self.assertEqual('%.10f' % resp.Center.Lat, '43.0034675598')
            self.assertEqual('%.10f' % resp.Center.Lon, '-92.9950942993')
    unittest.main()