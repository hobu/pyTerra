import unittest

from pyTerra import api, image
import datetime


class Object:
    pass
    
    
imagePresence='true'
MaxItems='10'
placeName='Ames'
theme = 'DOQ'
scale = "Scale4m"
ptype = 'CityTown'


# 
# #Extended around Baker field
# if large:
#     ul_x = 433714.25
#     ul_y = 4661043.80
#     lr_x = 438603.35
#     lr_y = 4656591.96
# else:
# #Baker field
#     ul_x = 436521.25
#     ul_y = 4659253.80
#     lr_x = 437142.35
#     lr_y = 4658582.96


lg_ul = Object()
lg_ul.X = 433714.25
lg_ul.Y = 4661043.80
lg_ul.Zone = 15

lg_lr = Object()
lg_lr.X = 438603.35
lg_lr.Y = 4656591.96
lg_lr.Zone = 15


ul = Object()
ul.X = 436521.25
ul.Y = 4659253.80
ul.Zone = 15

lr = Object()
lr.X = 436521.25
lr.Y = 4659253.80
lr.Zone = 15

scale = 'Scale2m'
theme = 'Ortho'
filename = 'test.jpg'

class ImageTest(unittest.TestCase):
    def testFetchSmallImage(self):
        """Fetching small image works"""
        img = image.TerraImage(ul, lr, scale, theme, lr.Zone, "/tmp")
        t = img.download()
        self.assertEqual(t.size[0], 200)
        self.assertEqual(t.size[1], 200)
        self.assertEqual(t.mode, 'RGB')
        dates = [datetime.datetime(1994, 4, 16, 0, 0)]
        self.assertEqual(img.dates, dates)

    def testFetchLargeImage(self):
        """Fetching large image works"""
        img = image.TerraImage(lg_ul, lg_lr, scale, theme, lr.Zone, "/tmp")
        t = img.download()
        self.assertEqual(t.size[0], 2600)
        self.assertEqual(t.size[1], 2400)
        self.assertEqual(t.mode, 'RGB')
        self.assertEqual(img.number_of_tiles, 156)

