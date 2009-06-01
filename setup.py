from distutils.core import setup
from distutils.core import Extension
import os, sys
f = os.path.abspath('.')
sys.path.append(f)

name="pyTerra"
version="0.6"
description="Terraserver Module for Python"
author="Howard Butler"
author_email="hobu@iastate.edu"
url="http://hobu.biz/software/pyTerra/"
   
setup(name=name,
      version=version,
      description=description,
      author=author,
      author_email=author_email,
      url=url,
      packages = ['pyTS', 'pyTS.SOAPpy', 'pyTS.SOAPpy.wstools', 'pyTS.TerraImage','pyTS.pyTerra']
      )