pyTerra: Python Support for the Microsoft TerraServer
------------------------------------------------------------------------------

pyTerra is a Python module that allows you to make requests to Microsoft's
TerraServer (http://msrmaps.com/).  With it, you can download
(older) cartographic images for any almost any geographic extent in the US.

The TerraServer has almost complete coverage of the United States for two very
important cartographic products, topographic maps and digital orthographic
photos (sometimes called DOQs or DOQQs).  You can find out more about DOQs here
(http://mapping.usgs.gov/www/ndop/) and more about what topographic maps are
here  (http://mac.usgs.gov/mac/isb/pubs/booklets/symbols/).  The TerraServer 
hasn't been updated in a number of years, and there are now many other imagery 
sources available, but the TerraServer was on of the first with nation-wide 
coverage. 

All methods reflect the TerraService API.  See the WSDL file at
http://msrmaps.com/TerraService2.asmx?WSDL for more information about how
to make the calls.

The TerraServer stores images as a pyramid of tiles.  Each tile is always 200
pixels square, independent of its actual ground resolution.  Aerial photos are
available in 1, 2, 4, 8, 16, 32, and 64 m resolutions.  Topographic maps are
available in all of the above resolutions except 1-meter.

Getting an image for an extent involves three steps: 1. Define a bounding box
for the area you want to download. A bounding box is a box defined by the upper
left point and lower left point of the box.  The point can be in geographic
coordinates (42.9332 deg N x -93.2112 deg W) or projected UTM coordinates
(437679.183 Easting and 4658340.891 Northing) 2. Make a request to the
TerraServer that returns all of the tiles that fall within the bounding box 3.
Make a request to the TerraServer for the image data in each tile and paste it
into a new PIL image.

History
..............................................................................

This version, 0.9, brings pyTerra up-to-date with a number of TerraServer 
changes that have happened in the past couple of years that I have not kept 
up with. The API has moved around a little bit to avoid confusion with the 
TerraServer USA commercial offering, and now that quad tree-based image 
caches are all the rage, TerraServer's SOAP API seems quite quaint. It 
does offer some unique things like metadata and a gazetteer which might 
make it useful in other contexts.  I had used pyTerra as the basis for avTerra, 
which was an ArcView 3.x extension for fetching TerraServer imagery. I 
suspect that pyTerra's lack of maintenance has meant avTerra is in disarray, 
but with this update, there's a possibility of it being brought back to life.  

The previous versions of this code were PSF-licensed, but that seems kind of 
silly. 0.9+ is now MIT, with the licensing text included in the source release 
as it should be. 

Otherwise, the effort to bring this codebase to modernity was mostly one 
of vanity, though I still have one or two things that still could use it. Looking 
at the code, it's hard to believe that it is nearly nine years old...

Changelog
..............................................................................

0.9 brings a number of changes to pyTerra. First, `SOAPpy`_ has been removed in 
exchange for `suds`_. Suds is much nicer than SOAPpy for simple tasks, and it 
handles the Microsoft WSDL like a champ. The movement to Suds simplified the 
internals quite a bit, and it should be much more straightforward to follow.

I have also modernized the ``setup.py`` and based it on `distribute`_, with 
dependencies of `PIL`_ and `suds`_ declared. Additionally, the unit tests, which 
had to be run manually are now available via a simple ``python setup.py test``
invocation.

Finally, the external API has been updated in a number of ways. These include
things like returning `datetime` instances where appropriate, PNG support,
etc. Having not heard of anyone using pyTerra in a number of years, I doubt
the API changes I have made will have much impact.

Usage
..............................................................................

pyTerra now contains two modules -- ``api`` and ``image``. These were formerly 
a messy module structure of TerraImage.TerraImage and pyTerra.pyTerra names. 

A short example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::
    
    from pyTerra import image
    
    class Object:
        pass

    lg_ul = Object()
    lg_ul.X = 433714.25
    lg_ul.Y = 4661043.80
    lg_ul.Zone = 15

    lg_lr = Object()
    lg_lr.X = 438603.35
    lg_lr.Y = 4656591.96
    lg_lr.Zone = 15

    scale = 'Scale2m'
    theme = 'Ortho' 

    img = image.TerraImage(ul, lr, scale, theme, lr.Zone, "/tmp")
    t = img.download() # <-- PIL.Image instance you can do what you need with
  

See ``pyTerra.image`` for more examples how to fetch imagery after fetching tile 
information. The tests/ directory also contains good example invocations of the 
various API methods and expected output of each.

.. _`SOAPpy`: http://pypi.python.org/pypi/SOAPpy
.. _`suds`: http://pypi.python.org/pypi/suds
.. _`distribute` : http://pypi.python.org/pypi/distribute
.. _`PIL`: http://pypi.python.org/pypi/PIL