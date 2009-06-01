"""
################################################################################
# Copyright (c) 2003, Pfizer
# Copyright (c) 2001, Cayce Ullman.
# Copyright (c) 2001, Brian Matthews.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# Neither the name of actzero, inc. nor the names of its contributors may
# be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
################################################################################
"""

ident = '$Id: Config.py,v 1.1 2003/10/01 02:00:27 hobu Exp $'

import copy
import socket
try: from M2Crypto import SSL
except: pass

from NS import NS 

################################################################################
# Configuration class
################################################################################

class SOAPConfig:
    __readonly = ('SSLserver', 'SSLclient')

    def __init__(self, config = None, **kw):
        d = self.__dict__

        if config:
            if not isinstance(config, SOAPConfig):
                raise AttributeError, \
                    "initializer must be SOAPConfig instance"

            s = config.__dict__

            for k, v in s.items():
                if k[0] != '_':
                    d[k] = v
        else:
            # Setting debug also sets returnFaultInfo, dumpFaultInfo,
            # dumpHeadersIn, dumpHeadersOut, dumpSOAPIn, and dumpSOAPOut
            self.debug = 0
            # Setting namespaceStyle sets typesNamespace, typesNamespaceURI,
            # schemaNamespace, and schemaNamespaceURI
            self.namespaceStyle = '1999'
            self.strictNamespaces = 0
            self.typed = 1
            self.buildWithNamespacePrefix = 1
            self.returnAllAttrs = 0


            # New argument name handling mechanism.  See
            # README.MethodParameterNaming for details
            self.specialArgs = 1

            try: SSL; d['SSLserver'] = 1
            except: d['SSLserver'] = 0

            try: socket.ssl; d['SSLclient'] = 1
            except: d['SSLclient'] = 0

        for k, v in kw.items():
            if k[0] != '_':
                setattr(self, k, v)

    def __setattr__(self, name, value):
        if name in self.__readonly:
            raise AttributeError, "readonly configuration setting"

        d = self.__dict__

        if name in ('typesNamespace', 'typesNamespaceURI',
            'schemaNamespace', 'schemaNamespaceURI'):

            if name[-3:] == 'URI':
                base, uri = name[:-3], 1
            else:
                base, uri = name, 0

            if type(value) == StringType:
                if NS.NSMAP.has_key(value):
                    n = (value, NS.NSMAP[value])
                elif NS.NSMAP_R.has_key(value):
                    n = (NS.NSMAP_R[value], value)
                else:
                    raise AttributeError, "unknown namespace"
            elif type(value) in (ListType, TupleType):
                if uri:
                    n = (value[1], value[0])
                else:
                    n = (value[0], value[1])
            else:
                raise AttributeError, "unknown namespace type"

            d[base], d[base + 'URI'] = n

            try:
                d['namespaceStyle'] = \
                    NS.STMAP_R[(d['typesNamespace'], d['schemaNamespace'])]
            except:
                d['namespaceStyle'] = ''

        elif name == 'namespaceStyle':
            value = str(value)

            if not NS.STMAP.has_key(value):
                raise AttributeError, "unknown namespace style"

            d[name] = value
            n = d['typesNamespace'] = NS.STMAP[value][0]
            d['typesNamespaceURI'] = NS.NSMAP[n]
            n = d['schemaNamespace'] = NS.STMAP[value][1]
            d['schemaNamespaceURI'] = NS.NSMAP[n]

        elif name == 'debug':
            d[name]                     = \
                d['returnFaultInfo']    = \
                d['dumpFaultInfo']      = \
                d['dumpHeadersIn']      = \
                d['dumpHeadersOut']     = \
                d['dumpSOAPIn']         = \
                d['dumpSOAPOut']        = value

        else:
            d[name] = value


Config = SOAPConfig()
