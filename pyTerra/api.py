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
# logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.getLogger('suds.client').setLevel(logging.ERROR)

lookup = {'DOQ':1, 'DRG':2, "ORTHO":1, "TOPO":2}

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
