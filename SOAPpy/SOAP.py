"""This file is here for backward compatibility with versions <= 0.9.9 

Delete when 1.0.0 is released!
"""

ident = '$Id: SOAP.py,v 1.1 2003/10/01 02:00:27 hobu Exp $'

from Client      import *
from Config      import *
from Errors      import *
from NS          import *
from Parser      import *
from SOAPBuilder import *
from Server      import *
from Types       import *
from Utilities     import *
import wstools
import WSDL

from warnings import warn

warn("""

The sub-module SOAPpy.SOAP is deprecated and is only
provided for short-term backward compatibility.  Objects are now
available directly within the SOAPpy module.  Thus, instead of

   from SOAPpy import SOAP
   ...
   SOAP.SOAPProxy(...)

use

   from SOAPpy import SOAPProxy
   ...
   SOAPProxy(...)

instead.
""", DeprecationWarning)
