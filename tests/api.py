import unittest
from pyTerra import * 



class Object:
    pass
    
    
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

base_logging_level = logging.ERROR
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
        """GetPlaceListInRect returns correct results"""
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
        logging.getLogger('suds.client').setLevel(logging.CRITICAL)
        self.assertRaises(pyTerraError,
                        GetPlaceFacts,
                        place)
        logging.getLogger('suds.client').setLevel(base_logging_level)
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


