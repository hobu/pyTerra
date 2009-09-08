"""Python API for the Microsoft TerraServer.
Copyright (c) 2003 Howard Butler hobu@hobu.net
This module requires a hacked version of SOAPpy (see http:\\hobu.biz\software\pyTerra\)
which is included in the module.
and pyXML 0.7 or greater.

*******************************************************************************
pyTerra: Python Support for the Microsoft TerraServer

*******************************************************************************
Version: 0.8

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

A hacked version of SOAPpy 0.12, which is packaged inside of pyTerra.
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

try:
    import pyTS.SOAPpy as SOAPpy
    from pyTS.SOAPpy import SOAPProxy
    from pyTS.SOAPpy import SOAPConfig
    from pyTS.SOAPpy import Types
except ImportError:
    import sys
    sys.path.append('..')
    import SOAPpy
    from SOAPpy import SOAPProxy
    from SOAPpy import SOAPConfig
    from SOAPpy import Types
import socket

__author__ = "Howard Butler  hobu@hobu.net"
__copyright__ ='(c) 2009 Howard Butler'
__version__= "0.8"

url = "http://terraservice.net/terraservice.asmx"
ns = "http://terraserver-usa.com/terraserver/"
debug = 0

retries = 2

class pyTerraError(Exception):
    """Custom exception for PyTerra"""
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)
    
def GetPlaceList(placeName, MaxItems, imagePresence="true"):
    """Returns a list of PlaceItems that have the same placeName"""
    sa = ns + 'GetPlaceList'
    server = SOAPProxy(url, namespace=ns, soapaction=sa, config=SOAPConfig(debug=debug))
    try:
        for i in range(retries):
            try:
                resp = server.GetPlaceList(imagePresence = imagePresence,
                                           MaxItems = MaxItems,
                                           placeName = placeName)
                if resp:
                    raise KeyError
            except socket.error , e:
                if e[0] == 10060:
                    continue
            except SOAPpy.Types.faultType, e:
                # reraise the KeyError as our indication of being done
                if isinstance(e, KeyError):
                    raise KeyError
                raise pyTerraError(e[1])
    except KeyError: #KeyError was raised, which means we're good to go
        pass

    if isinstance (resp, Types.faultType):
        raise pyTerraError(resp.faultstring)
    else:
        return resp

def GetPlaceListInRect(upperLeft, lowerRight, ptype, MaxItems):
    """Returns a list of places inside the bounding box"""
    #This function is not known to return good results
    sa = ns + 'GetPlaceListInRect'
    server = SOAPProxy(url, namespace=ns, soapaction=sa, config=SOAPConfig(debug=debug))
    try:
        for i in range(retries):
            try:
                resp = server.GetPlaceListInRect(upperLeft = upperLeft,
                                              lowerRight = lowerRight,
                                              ptype = ptype,
                                              MaxItems = MaxItems)
                if resp:
                    raise KeyError
            except socket.error , e:
                if e[0] == 10060:
                    continue
            except SOAPpy.Types.faultType, e:
                # reraise the KeyError as our indication of being done
                if isinstance(e, KeyError):
                    raise KeyError
                raise pyTerraError(e[1])
    except KeyError: #KeyError was raised, which means we're good to go
        pass

    if isinstance (resp, Types.faultType):
        raise pyTerraError(resp.faultstring)
    else:
        return resp

def GetPlaceFacts(place):
    """Gets facts about a place (park, CityTown, etc..)"""
    sa = ns + 'GetPlaceFacts'
    server = SOAPProxy(url, namespace=ns, soapaction=sa, config=SOAPConfig(debug=debug))
    try:
        for i in range(retries):
            try:
                resp = server.GetPlaceFacts(place = place)
                if resp:
                    raise KeyError
            except socket.error , e:
                if e[0] == 10060:
                    continue
            except SOAPpy.Types.faultType, e:
                # reraise the KeyError as our indication of being done
                if isinstance(e, KeyError):
                    raise KeyError
                raise pyTerraError(e[1])
    except KeyError: #KeyError was raised, which means we're good to go
        pass
    
    if isinstance (resp, Types.faultType):
        raise pyTerraError(resp.faultstring)
    else:
        return resp
    
def GetAreaFromPt(center, theme, scale, displayPixWidth, displayPixHeight):
    """Returns an area (set of tiles) defined by a point"""
    sa = ns + 'GetAreaFromPt'
    server = SOAPProxy(url, namespace=ns, soapaction=sa, config=SOAPConfig(debug=debug))
    try:
        for i in range(retries):
            try:
                resp = server.GetAreaFromPt(center = center,displayPixHeight = displayPixHeight,
                                           displayPixWidth = displayPixWidth,
                                           scale = scale,
                                           theme = theme,
                                           )
                
                if resp:
                    raise KeyError
            except socket.error , e:
                if e[0] == 10060:
                    continue
            except SOAPpy.Types.faultType, e:
                # reraise the KeyError as our indication of being done
                if isinstance(e, KeyError):
                    raise KeyError
                raise pyTerraError(e[1])
    except KeyError: #KeyError was raised, which means we're good to go
        pass

    if isinstance (resp, Types.faultType):
        raise pyTerraError(resp.faultstring)
    else:
        return resp

def GetAreaFromTileId(id):
    """Returns the bounding box for a TileMeta.Id"""
    sa = ns + 'GetAreaFromTileId'
    server = SOAPProxy(url, namespace=ns, soapaction=sa, config=SOAPConfig(debug=debug))
    try:
        for i in range(retries):
            try:
                resp = server.GetAreaFromTileId(id=id)
                if resp:
                    raise KeyError
            except socket.error , e:
                if e[0] == 10060:
                    continue
            except SOAPpy.Types.faultType, e:
                # reraise the KeyError as our indication of being done
                if isinstance(e, KeyError):
                    raise KeyError
                raise pyTerraError(e[1])
    except KeyError: #KeyError was raised, which means we're good to go
        pass

    if isinstance (resp, Types.faultType):
        raise pyTerraError(resp.faultstring)
    else:
        return resp
    
    if isinstance (resp, Types.faultType):
        raise pyTerraError(resp.faultstring)
    else:
        return resp

def GetAreaFromRect(upperLeft, lowerRight, theme, scale):
    """Returns the tiles for the bounding box defined by upperLeft and lowerRight"""
    sa = ns + 'GetAreaFromRect'
    server = SOAPProxy(url, namespace=ns, soapaction=sa, config=SOAPConfig(debug=debug))
    try:
        for i in range(retries):
            try:
                resp = server.GetAreaFromRect(upperLeft = upperLeft,
                                              lowerRight = lowerRight,
                                              theme = theme,
                                              scale = scale)
                if resp:
                    raise KeyError
            except socket.error , e:
                if e[0] == 10060:
                    continue
            except SOAPpy.Types.faultType, e:
                # reraise the KeyError as our indication of being done
                if isinstance(e, KeyError):
                    raise KeyError
                raise pyTerraError(e[1])
    except KeyError: #KeyError was raised, which means we're good to go
        pass

    if isinstance (resp, Types.faultType):
        raise pyTerraError(resp.faultstring)
    else:
        return resp
    
def GetTileMetaFromTileId(id):
    """Gets the metadata for a TileMeta.Id"""
    sa = ns + 'GetTileMetaFromTileId'
    server = SOAPProxy(url, namespace=ns, soapaction=sa, config=SOAPConfig(debug=debug))
    try:
        for i in range(retries):
            try:
                resp = server.GetTileMetaFromTileId(id = id)
                if resp:
                    raise KeyError
            except socket.error , e:
                if e[0] == 10060:
                    continue
            except SOAPpy.Types.faultType, e:
                # reraise the KeyError as our indication of being done
                if isinstance(e, KeyError):
                    raise KeyError
                raise pyTerraError(e[1])
    except KeyError: #KeyError was raised, which means we're good to go
        pass
    
    if isinstance (resp, Types.faultType):
        raise pyTerraError(resp.faultstring)
    else:
        return resp

def GetTileMetaFromLonLatPt(point, theme, scale):
    """Gets the TileMeta for a point (lat/lon)"""
    sa = ns + 'GetTileMetaFromLonLatPt'
    server = SOAPProxy(url, namespace=ns, soapaction=sa, config=SOAPConfig(debug=debug))
    try:
        for i in range(retries):
            try:
                resp = server.GetTileMetaFromLonLatPt(point = point,
                                              theme = theme,
                                              scale = scale)
                if resp:
                    raise KeyError
            except socket.error , e:
                if e[0] == 10060:
                    continue
            except SOAPpy.Types.faultType, e:
                # reraise the KeyError as our indication of being done
                if isinstance(e, KeyError):
                    raise KeyError
                raise pyTerraError(e[1])
    except KeyError: #KeyError was raised, which means we're good to go
        pass
    if isinstance (resp, Types.faultType):
        raise pyTerraError(resp.faultstring)
    else:
        return resp

def GetTile(id):
    """Returns the tile image data"""
    sa = ns + 'GetTile'
    server = SOAPProxy(url, namespace=ns, soapaction=sa, config=SOAPConfig(debug=debug))
    try:
        for i in range(retries):
            try:
                resp = server.GetTile(id = id)
                if resp:
                    raise KeyError
            except socket.error , e:
                if e[0] == 10060:
                    continue
            except SOAPpy.Types.faultType, e:
                # reraise the KeyError as our indication of being done
                if isinstance(e, KeyError):
                    raise KeyError
                raise pyTerraError(e[1])
    except KeyError: #KeyError was raised, which means we're good to go
        pass
    if isinstance (resp, Types.faultType):
        raise pyTerraError(resp.faultstring)
    else:
        return resp

def ConvertLonLatPtToNearestPlace(point):
    """Converts a lat/lon point into a place"""
    sa = ns + 'ConvertLonLatPtToNearestPlace'
    server = SOAPProxy(url, namespace=ns, soapaction=sa, config=SOAPConfig(debug=debug))
    try:
        for i in range(retries):
            try:
                resp = server.ConvertLonLatPtToNearestPlace(point = point)
                if resp:
                    raise KeyError
            except socket.error , e:
                if e[0] == 10060:
                    continue
            except SOAPpy.Types.faultType, e:
                # reraise the KeyError as our indication of being done
                if isinstance(e, KeyError):
                    raise KeyError
                raise pyTerraError(e[1])
    except KeyError: #KeyError was raised, which means we're good to go
        pass
    
    if isinstance (resp, Types.faultType):
        raise pyTerraError(resp.faultstring)
    else:
        return resp

def ConvertUtmPtToLonLatPt(utm):
    """Converts a UTM point into lat/lon"""
    sa = ns + 'ConvertUtmPtToLonLatPt'
    server = SOAPProxy(url, namespace=ns, soapaction=sa, config=SOAPConfig(debug=debug))
    try:
        for i in range(retries):
            try:
                resp = server.ConvertUtmPtToLonLatPt(utm = utm)
                if resp:
                    raise KeyError
            except socket.error , e:
                if e[0] == 10060:
                    continue
            except SOAPpy.Types.faultType, e:
                # reraise the KeyError as our indication of being done
                if isinstance(e, KeyError):
                    raise KeyError
                import pdb;pdb.set_trace()
                raise pyTerraError(e[1])
    except KeyError: #KeyError was raised, which means we're good to go
        pass
    if isinstance (resp, Types.faultType):
        raise pyTerraError(resp.faultstring)
    else:
        return resp

def ConvertLonLatPtToUtmPt(point):
    """Converts a lat/lon point into UTM"""
    sa = ns + 'ConvertLonLatPtToUtmPt'
    server = SOAPProxy(url, namespace=ns, soapaction=sa, config=SOAPConfig(debug=debug))
    try:
        for i in range(retries):
            try:
                resp = server.ConvertLonLatPtToUtmPt(point = point)
                if resp:
                    raise KeyError
            except socket.error , e:
                if e[0] == 10060:
                    continue
            except SOAPpy.Types.faultType, e:
                # reraise the KeyError as our indication of being done
                if isinstance(e, KeyError):
                    raise KeyError
                raise pyTerraError(e[1])
    except KeyError: #KeyError was raised, which means we're good to go
        pass

    if isinstance (resp, Types.faultType):
        raise pyTerraError(resp.faultstring)
    else:
        return resp

def ConvertPlaceToLonLatPt(place):
    """Converts a place struct into a lat/lon point"""
    sa = ns + 'ConvertPlaceToLonLatPt'
    server = SOAPProxy(url, namespace=ns, soapaction=sa, config=SOAPConfig(debug=debug))
    try:
        for i in range(retries):
            try:
                resp = server.ConvertPlaceToLonLatPt(place = place)
                if resp:
                    raise KeyError
            except socket.error , e:
                if e[0] == 10060:
                    continue
            except SOAPpy.Types.faultType, e:
                # reraise the KeyError as our indication of being done
                if isinstance(e, KeyError):
                    raise KeyError
                raise pyTerraError(e[1])
    except KeyError: #KeyError was raised, which means we're good to go
        pass

    if isinstance (resp, Types.faultType):
        raise pyTerraError(resp.faultstring)
    else:
        return resp

def GetTheme(theme):
    """Returns theme information about a theme (Photo, Topo, or Relief)"""
    sa = ns + 'GetTheme'
    server = SOAPProxy(url, namespace=ns, soapaction=sa, config=SOAPConfig(debug=debug))
    try:
        for i in range(retries):
            try:
                resp = server.GetTheme(theme)
                if resp:
                    raise KeyError
            except socket.error , e:
                if e[0] == 10060:
                    continue
            except SOAPpy.Types.faultType, e:
                # reraise the KeyError as our indication of being done
                if isinstance(e, KeyError):
                    raise KeyError
                raise pyTerraError(e[1])
    except KeyError: #KeyError was raised, which means we're good to go
        pass

    if isinstance (resp, Types.faultType):
        raise pyTerraError(resp.faultstring)
    else:
        return resp

def GetLatLonMetrics(point):
    """Don't know why this is there or what this does"""
    sa = ns + 'GetLatLonMetrics'
    server = SOAPProxy(url, namespace=ns, soapaction=sa, config=SOAPConfig(debug=debug))
    try:
        for i in range(retries):
            try:
                resp = server.GetLatLonMetrics(point = point)
                if resp:
                    raise KeyError
            except socket.error , e:
                if e[0] == 10060:
                    continue
            except SOAPpy.Types.faultType, e:
                # reraise the KeyError as our indication of being done
                if isinstance(e, KeyError):
                    raise KeyError
                raise pyTerraError(e[1])
    except KeyError: #KeyError was raised, which means we're good to go
        pass

    if isinstance (resp, Types.faultType):
        raise pyTerraError(resp.faultstring)
    else:
        return resp
    
def CountPlacesInRect(upperLeft, lowerRight, ptype):
    """Counts the number of places inside the bounding box with the specified ptype"""
    sa = ns + 'CountPlacesInRect'
    server = SOAPProxy(url, namespace=ns, soapaction=sa, config=SOAPConfig(debug=debug))
    try:
        for i in range(retries):
            try:
                resp = server.CountPlacesInRect(upperLeft = upperLeft,
                                              lowerRight = lowerRight,
                                              ptype = ptype)
                if resp:
                    raise KeyError
            except socket.error , e:
                if e[0] == 10060:
                    continue
            except SOAPpy.Types.faultType, e:
                # reraise the KeyError as our indication of being done
                if isinstance(e, KeyError):
                    raise KeyError
                raise pyTerraError(e[1])
    except KeyError: #KeyError was raised, which means we're good to go
        pass

    if isinstance (resp, Types.faultType):
        raise pyTerraError(resp.faultstring)
    else:
        return resp

if __name__ == '__main__':
    
    import unittest
    import sys
    imagePresence='true'
    MaxItems='10'
    placeName='Ames'
    theme = "Photo"
    scale = "Scale4m"
    ptype = 'CityTown'

    displayPixWidth = 200
    displayPixHeight = 200

    place = Types.structType(name=(ns,'ns1'))
    place.City = 'Ames'
    place.State = 'Iowa'
    place.Country = 'United States'

    pt = Types.structType(name=(ns,'ns1'))
    pt.Lon = -93.000
    
    pt.Lat = 43.000
    center = pt

    upperLeft = Types.structType(name=(ns,'ns1'))
    upperLeft.Lon = -93.000
    upperLeft.Lat = 43.000
    
    lowerRight = Types.structType(name=(ns,'ns1'))
    lowerRight.Lon = -92.8999
    lowerRight.Lat = 42.8999
    # 
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
            expected_x = '624'
            expected_y = '5951'
            expected_date = '1994-04-23'
            self.assertEqual(id.Y, expected_y)
            self.assertEqual(id.X, expected_x)
            self.assertEqual(resp.NorthWest.TileMeta.Capture[:10], expected_date)
        def testGetPlaceListassert(self):
            """GetPlaceList traps bad inputs"""
            self.assertRaises(pyTerraError,
                              GetPlaceList,
                              placeName, 'aabbcc', imagePresence)
            self.assertRaises(pyTerraError,
                              GetPlaceList,
                              placeName, MaxItems, 'falsse')
        def testGetPlaceListequals(self):
            """GetPlaceList returns Ames, Iowa as first result"""
            resp = GetPlaceList(placeName, MaxItems, imagePresence)
            ames = resp.PlaceFacts[0]
            self.assertEqual(ames.Place.State,"Iowa")
            self.assertEqual(ames.Place.City,"Ames")
        def testConvertLonLatPtToNearestPlaceassert(self):
            """ConvertLonLatPtToNearestPlace traps bad inputs"""
            pt.Lat = 'abc'
            self.assertRaises(pyTerraError,
                              ConvertLonLatPtToNearestPlace,
                              pt)
        def testConvertLonLatPtToNearestPlaceequals(self):
            """ConvertLonLatPtToNearestPlace returns 7 km SW of Rockford, Iowa"""
          #  import pdb;pdb.set_trace()
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
            expected_x = '500000'
            expected_y = '4760814.7962907264'
            expected_zone = '15'
            self.assertEqual(resp.X, expected_x)
            self.assertEqual(resp.Y, expected_y)
            self.assertEqual(resp.Zone, expected_zone)
        def testConvertLonLatPtToUtmPtassert(self):
            """ConvertLonLatPtToUtmPt traps bad inputs"""
            pt.Lat = 'abc'
            self.assertRaises(pyTerraError,
                              ConvertLonLatPtToUtmPt,
                              pt)       
        def testGetTileMetaFromTileIdassert(self):
            """GetTileMetaFromTileId traps bad inputs"""
            id = Types.structType()
            id.X = 'abc'
            id.Y = '5951'
            id.scene = '15'
            id.theme = theme
            id.scale = scale
            self.assertRaises(pyTerraError,
                              GetTileMetaFromTileId,
                              id)
        def testGetTileMetaFromTileIdtequals(self):
            """GetTileMetaFromTileId returns correct results"""
            resp = GetAreaFromPt(center, theme, scale, displayPixWidth, displayPixHeight)
            id = resp.NorthWest.TileMeta.Id
            resp = GetTileMetaFromTileId(id)
            self.assertEqual(resp.NorthWest.Lat, '43.0070686340332')
            self.assertEqual(resp.NorthWest.Lon, '-93.009819030761719')
        def testGetAreaFromTileIdassert(self):
            """GetAreaFromTileId traps bad inputs"""
            id = Types.structType(name=(ns,'ns1'))
            id.X = 'abc'
            id.Y = '5951'
            id.scene = '15'
            id.theme = theme
            id.scale = scale
            self.assertRaises(pyTerraError,
                              GetAreaFromTileId,
                              id)
        def testGetAreaFromTileIdequals(self):
            """GetAreaFromTileId returns correct results"""
            id = Types.structType(name=(ns,'ns1'))
            id.X = '624'
            id.Y = '5951'
            id.Scene = '15'
            id.Theme = theme
            id.Scale = scale
            resp = GetAreaFromTileId(id)
            self.assertEqual(resp.NorthWest.TileMeta.NorthWest.Lat, '43.014274597167969')
            self.assertEqual(resp.NorthWest.TileMeta.NorthWest.Lon, '-93.019638061523438')
        def testGetTileassert(self):
            """GetTile traps bad inputs"""
            id = Types.structType(name=(ns,'ns1'))
            id.X = 'abc'
            id.Y = '5951'
            id.Scene = '15'
            id.Theme = theme
            id.Scale = scale
            self.assertRaises(pyTerraError,
                              GetTile,
                              id)
        def testGetTileequals(self):
            """GetTile returns correct results"""
            id = Types.structType(name=(ns,'ns1'))
            id.X = '624'
            id.Y = '5951'
            id.Scene = '15'
            id.Theme = theme
            id.Scale = scale
            resp = GetTile(id)
            self.assertEqual(len(resp), 6942)
        def testConvertUtmPtToLonLatPtassert(self):
            """ConvertUtmPtToLonLatPt traps bad inputs"""
            utm = Types.structType(name=(ns,'ns1'))
            utm.X = 'abc'
            utm.Y = '4760814.7962907264'
            utm.Zone = '15'
            self.assertRaises(pyTerraError,
                              ConvertUtmPtToLonLatPt,
                              utm)
        def testConvertUtmPtToLonLatPtequals(self):
            """ConvertUtmPtToLonLatPt returns correct results"""
            utm = Types.structType(name=(ns,'ns1'))
            utm.X = '500000'
            utm.Y = '4760814.7962907264'
            utm.Zone = '15'
            resp = ConvertUtmPtToLonLatPt(utm)
            self.assertEqual(resp.Lat, '42.999999999999943')
            self.assertEqual(resp.Lon, '-92.9999999999999')
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
            self.assertEqual(resp.NorthWest.TileMeta.NorthWest.Lat, '43.007072448730469')
            self.assertEqual(resp.NorthWest.TileMeta.NorthWest.Lon, '-93')
        def testGetLatLonMetricsassert(self):
            """GetLatLonMetrics traps bad inputs"""
            upperLeft.Lat = 'abc'
            self.assertRaises(pyTerraError,
                              GetLatLonMetrics,
                              upperLeft)
        def testGetPlaceListInRectassert(self):
          """GetPlaceListInRect traps bad inputs"""
          self.assertRaises(pyTerraError,
                            GetPlaceListInRect,
                            upperLeft,
                            lowerRight,
                            'abc',
                            MaxItems)
        def testGetPlaceFactsassert(self):
          """GetPlaceFacts traps bad inputs"""
          place.City = 43.200
          self.assertRaises(pyTerraError,
                            GetPlaceFacts,
                            place)
        def testGetPlaceFactsequals(self):
            """GetPlaceFacts returns correct results"""
            place = Types.structType(name=(ns,'ns1'))
            place.City = 'Ames'
            place.State = 'Iowa'
            place.Country = 'United States'
            resp = GetPlaceFacts(place)
            self.assertEqual(resp.Center.Lat, '42.029998779296875')
            self.assertEqual(resp.Center.Lon, '-93.610000610351562')
        def testGetTileMetaFromLonLatPtassert(self):
          """GetTileMetaFromLonLatPt traps bad inputs"""
          self.assertRaises(pyTerraError,
                            GetTileMetaFromLonLatPt,
                            pt,
                            'Photos',
                            scale)
        def testGetTileMetaFromLonLatPtequals(self):
            """GetTileMetaFromLonLatPt returns correct results"""
            resp = GetTileMetaFromLonLatPt(pt, theme, scale)
            self.assertEqual(resp.Center.Lat, '43.003467559814453')
            self.assertEqual(resp.Center.Lon, '-92.9950942993164')
    unittest.main()