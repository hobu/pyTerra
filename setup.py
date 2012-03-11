import warnings

try:
    from distribute_setup import use_setuptools
    use_setuptools()
except:
    warnings.warn(
    "Failed to import distribute_setup, continuing without distribute.", 
    Warning)
    
try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup, Extension
    

import pyTerra
name="pyTerra"
version=pyTerra.__version__
description="Terraserver Module for Python"
author="Howard Butler"
author_email="hobu.inc@gmail.com"
url="http://github.com/hobu/pyterra/"


classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
        
]

readme_text = file('README.rst', 'rb').read()

setup(name=name,
      version=version,
      description=description,
      long_description = readme_text,
      author=author,
      author_email=author_email,
      url=url,
      classifiers = classifiers,
      install_requires= ['suds>=0.4','PIL>=1.1.4'],
      packages = ['pyTerra'],
      test_suite="tests"
      )
