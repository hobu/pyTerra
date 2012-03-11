import unittest

from pyTerra import api, image



class Object:
    pass
    
    
imagePresence='true'
MaxItems='10'
placeName='Ames'
theme = 1
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

ul = Object()
ul.X = 436521.25
ul.Y = 4659253.80
ul.Zone = 15

lr = Object()
lr.X = 436521.25
lr.Y = 4659253.80
lr.Zone = 15

scale = 'Scale2m'
theme = 'Topo'
filename = 'test.jpg'

class ImageTest(unittest.TestCase):
    def testFetchImage(self):
        """Fetching base image works"""
        pass
