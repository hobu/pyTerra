try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup, Extension
    

name="pyTerra"
version="0.8"
description="Terraserver Module for Python"
author="Howard Butler"
author_email="hobu.inc@gmail.com"
url="http://bitbucket.org/hobu/pyterra/"


classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
        
]


setup(name=name,
      version=version,
      description=description,
      author=author,
      author_email=author_email,
      url=url,
      classifiers = classifiers,
      packages = ['pyTerra.SOAPpy', 'pyTerra.SOAPpy.wstools', 'pyTerra.TerraImage','pyTerra.pyTerra','pyTerra']
      )
