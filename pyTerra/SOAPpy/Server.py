"""
################################################################################
#
# SOAPpy - Cayce Ullman       (cayce@actzero.com)
#          Brian Matthews     (blm@actzero.com)
#          Gregory Warnes     (gregory_r_warnes@groton.pfizer.com)
#          Christopher Blunck (blunck@gst.com)
#
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

from __future__ import nested_scopes

#import xml.sax
import re
import socket
import sys
import SocketServer
from types import *
import BaseHTTPServer

# SOAPpy modules
from Parser      import parseSOAPRPC
from Config      import Config
from Types       import faultType, voidType
from NS          import NS
from SOAPBuilder import buildSOAP
from Utilities   import debugHeader, debugFooter

try: from M2Crypto import SSL
except: pass

ident = '$Id: Server.py,v 1.1 2003/10/01 02:00:27 hobu Exp $'

from version import __version__



################################################################################
# Server
################################################################################

# Method Signature class for adding extra info to registered funcs, right now
# used just to indicate it should be called with keywords, instead of ordered
# params.
class MethodSig:
    def __init__(self, func, keywords=0, context=0):
        self.func     = func
        self.keywords = keywords
        self.context  = context
        self.__name__ = func.__name__

    def __call__(self, *args, **kw):
        return apply(self.func,args,kw)

class SOAPContext:
    def __init__(self, header, body, attrs, xmldata, connection, httpheaders,
        soapaction):

        self.header     = header
        self.body       = body
        self.attrs      = attrs
        self.xmldata    = xmldata
        self.connection = connection
        self.httpheaders= httpheaders
        self.soapaction = soapaction

# A class to describe how header messages are handled
class HeaderHandler:
    # Initially fail out if there are any problems.
    def __init__(self, header, attrs):
        for i in header.__dict__.keys():
            if i[0] == "_":
                continue

            d = getattr(header, i)

            try:
                fault = int(attrs[id(d)][(NS.ENV, 'mustUnderstand')])
            except:
                fault = 0

            if fault:
                raise faultType, ("%s:MustUnderstand" % NS.ENV_T,
                    "Don't understand `%s' header element but "
                    "mustUnderstand attribute is set." % i)




################################################################################
# SOAP Server
################################################################################
class SOAPServerBase:

    def get_request(self):
        sock, addr = get_request(self)

        if self.ssl_context:
            sock = SSL.Connection(self.ssl_context, sock)
            sock._setup_ssl(addr)
            if sock.accept_ssl() != 1:
                raise socket.error, "Couldn't accept SSL connection"

        return sock, addr

    def registerObject(self, object, namespace = ''):
        if namespace == '': namespace = self.namespace
        self.objmap[namespace] = object

    def registerFunction(self, function, namespace = '', funcName = None):
        if not funcName : funcName = function.__name__
        if namespace == '': namespace = self.namespace
        if self.funcmap.has_key(namespace):
            self.funcmap[namespace][funcName] = function
        else:
            self.funcmap[namespace] = {funcName : function}

    def registerKWObject(self, object, namespace = ''):
        if namespace == '': namespace = self.namespace
        for i in dir(object.__class__):
            if i[0] != "_" and callable(getattr(object, i)):
                self.registerKWFunction(getattr(object,i), namespace)

    # convenience  - wraps your func for you.
    def registerKWFunction(self, function, namespace = '', funcName = None):
        self.registerFunction(MethodSig(function,keywords=1), namespace,
        funcName)


class SOAPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def version_string(self):
        return '<a href="http://pywebsvcs.sf.net">' + \
            'SOAPpy ' + __version__ + '</a> (Python ' + \
            sys.version.split()[0] + ')'

    def date_time_string(self):
        self.__last_date_time_string = \
            BaseHTTPServer.BaseHTTPRequestHandler.\
            date_time_string(self)

        return self.__last_date_time_string

    def do_POST(self):
        status = 500
        try:
            if self.server.config.dumpHeadersIn:
                s = 'Incoming HTTP headers'
                debugHeader(s)
                print self.raw_requestline.strip()
                print "\n".join(map (lambda x: x.strip(),
                    self.headers.headers))
                debugFooter(s)

            data = self.rfile.read(int(self.headers["content-length"]))
            #            data = data.encode('ascii','replace')

            if self.server.config.dumpSOAPIn:
                s = 'Incoming SOAP'
                debugHeader(s)
                print data,
                if data[-1] != '\n':
                    print
                debugFooter(s)

            (r, header, body, attrs) = \
                parseSOAPRPC(data, header = 1, body = 1, attrs = 1)

            method = r._name
            args   = r._aslist
            kw     = r._asdict
            
            # Handle mixed named and unnamed arguments by assuming
            # that all arguments with names of the form "_[0-9]+"
            # are unnamed and should be passed in numeric order,
            # other arguments are named and should be passed using
            # this name.  This is a custom exension to the SOAP
            # protocol, and is thus disabled by default.  To
            # enable, set Config.specialArgs to a true value.

            if Config.specialArgs: 
                
                ordered_args = {}
                named_args   = {}
                
                for (k,v) in  kw.items():
                    m = re.match("_([0-9]+)", k)
                    if m is None:
                        named_args[str(k)] = v
                    else:
                        ordered_args[int(m.group(1))] = v
                        
                keylist = ordered_args.keys()
                keylist.sort()
                tmp = map( lambda x: ordered_args[x], keylist)

                ordered_args = tmp

                #print '<-> Argument Matching Yielded:'
                #print '<-> Ordered Arguments:' + str(ordered_args)
                #print '<-> Named Arguments  :' + str(named_args)
             

            ns = r._ns
            resp = ""
            # For fault messages
            if ns:
                nsmethod = "%s:%s" % (ns, method)
            else:
                nsmethod = method

            try:
                # First look for registered functions
                if self.server.funcmap.has_key(ns) and \
                    self.server.funcmap[ns].has_key(method):
                    f = self.server.funcmap[ns][method]
                else: # Now look at registered objects
                    # Check for nested attributes. This works even if
                    # there are none, because the split will return
                    # [method]
                    f = self.server.objmap[ns]
                    l = method.split(".")
                    for i in l:
                        f = getattr(f, i)
            except:
                resp = buildSOAP(faultType("%s:Client" % NS.ENV_T,
                        "No method %s found" % nsmethod,
                        "%s %s" % tuple(sys.exc_info()[0:2])),
                    encoding = self.server.encoding,
                    config = self.server.config)
                status = 500
            else:
                try:
                    if header:
                        x = HeaderHandler(header, attrs)

                    # If it's wrapped, some special action may be needed
                    
                    if isinstance(f, MethodSig):
                        c = None
                    
                        if f.context:  # Build context object
                            c = SOAPContext(header, body, attrs, data,
                                self.connection, self.headers,
                                self.headers["soapaction"])

                        if Config.specialArgs:
                            if c:
                                named_args["_SOAPContext"] = c
                            fr = apply(f, ordered_args, named_args)
                        elif f.keywords:
                            # This is lame, but have to de-unicode
                            # keywords
                            
                            strkw = {}
                            
                            for (k, v) in kw.items():
                                strkw[str(k)] = v
                            if c:
                                strkw["_SOAPContext"] = c
                            fr = apply(f, (), strkw)
                        elif c:
                            fr = apply(f, args, {'_SOAPContext':c})
                        else:
                            fr = apply(f, args, {})

                    else:
                        if Config.specialArgs:
                            fr = apply(f, ordered_args, named_args)
                        else:
                            fr = apply(f, args, {})

                    
                    if type(fr) == type(self) and \
                        isinstance(fr, voidType):
                        resp = buildSOAP(kw = {'%sResponse' % method: fr},
                            encoding = self.server.encoding,
                            config = self.server.config)
                    else:
                        resp = buildSOAP(kw =
                            {'%sResponse' % method: {'Result': fr}},
                            encoding = self.server.encoding,
                            config = self.server.config)
                except Exception, e:
                    import traceback
                    info = sys.exc_info()

                    if self.server.config.dumpFaultInfo:
                        s = 'Method %s exception' % nsmethod
                        debugHeader(s)
                        traceback.print_exception(info[0], info[1],
                            info[2])
                        debugFooter(s)

                    if isinstance(e, faultType):
                        f = e
                    else:
                        f = faultType("%s:Server" % NS.ENV_T,
                           "Method %s failed." % nsmethod)

                    if self.server.config.returnFaultInfo:
                        f._setDetail("".join(traceback.format_exception(
                                info[0], info[1], info[2])))
                    elif not hasattr(f, 'detail'):
                        f._setDetail("%s %s" % (info[0], info[1]))

                    resp = buildSOAP(f, encoding = self.server.encoding,
                       config = self.server.config)
                    status = 500
                else:
                    status = 200
        except faultType, e:
            import traceback
            info = sys.exc_info()

            if self.server.config.dumpFaultInfo:
                s = 'Received fault exception'
                debugHeader(s)
                traceback.print_exception(info[0], info[1],
                    info[2])
                debugFooter(s)

            if self.server.config.returnFaultInfo:
                e._setDetail("".join(traceback.format_exception(
                        info[0], info[1], info[2])))
            elif not hasattr(e, 'detail'):
                e._setDetail("%s %s" % (info[0], info[1]))

            resp = buildSOAP(e, encoding = self.server.encoding,
                config = self.server.config)
            status = 500
        except Exception, e:
            # internal error, report as HTTP server error

            if self.server.config.dumpFaultInfo:
                s = 'Internal exception %s' % e
                import traceback
                debugHeader(s)
                info = sys.exc_info()
                traceback.print_exception(info[0], info[1],
                                          info[2])
                debugFooter(s)

            self.send_response(500)
            self.end_headers()

            if self.server.config.dumpHeadersOut and \
                self.request_version != 'HTTP/0.9':
                s = 'Outgoing HTTP headers'
                debugHeader(s)
                if self.responses.has_key(status):
                    s = ' ' + self.responses[status][0]
                else:
                    s = ''
                print "%s %d%s" % (self.protocol_version, 500, s)
                print "Server:", self.version_string()
                print "Date:", self.__last_date_time_string
                debugFooter(s)
        else:
            # got a valid SOAP response
            self.send_response(status)

            t = 'text/xml';
            if self.server.encoding != None:
                t += '; charset="%s"' % self.server.encoding
            self.send_header("Content-type", t)
            self.send_header("Content-length", str(len(resp)))
            self.end_headers()

            if self.server.config.dumpHeadersOut and \
                self.request_version != 'HTTP/0.9':
                s = 'Outgoing HTTP headers'
                debugHeader(s)
                if self.responses.has_key(status):
                    s = ' ' + self.responses[status][0]
                else:
                    s = ''
                print "%s %d%s" % (self.protocol_version, status, s)
                print "Server:", self.version_string()
                print "Date:", self.__last_date_time_string
                print "Content-type:", t
                print "Content-length:", len(resp)
                debugFooter(s)

            if self.server.config.dumpSOAPOut:
                s = 'Outgoing SOAP'
                debugHeader(s)
                print resp,
                if resp[-1] != '\n':
                    print
                debugFooter(s)

            self.wfile.write(resp)
            self.wfile.flush()

            # We should be able to shut down both a regular and an SSL
            # connection, but under Python 2.1, calling shutdown on an
            # SSL connections drops the output, so this work-around.
            # This should be investigated more someday.

            if self.server.config.SSLserver and \
                isinstance(self.connection, SSL.Connection):
                self.connection.set_shutdown(SSL.SSL_SENT_SHUTDOWN |
                    SSL.SSL_RECEIVED_SHUTDOWN)
            else:
                self.connection.shutdown(1)

        def do_GET(self):

            #print 'command        ', self.command
            #print 'path           ', self.path
            #print 'request_version', self.request_version
            #print 'headers'
            #print '   type    ', self.headers.type
            #print '   maintype', self.headers.maintype
            #print '   subtype ', self.headers.subtype
            #print '   params  ', self.headers.plist

            path = self.path.lower()
            if path.endswith('wsdl'):
                method = 'wsdl'
                function = namespace = None
                if self.server.funcmap.has_key(namespace) \
                        and self.server.funcmap[namespace].has_key(method):
                    function = self.server.funcmap[namespace][method]
                else: 
                    if namespace in self.server.objmap.keys():
                        function = self.server.objmap[namespace]
                        l = method.split(".")
                        for i in l:
                            function = getattr(function, i)

                if function:
                    self.send_response(200)
                    self.send_header("Content-type", 'text/plain')
                    self.end_headers()
                    response = apply(function, ())
                    self.wfile.write(str(response))
                    return

            # return error
            self.send_response(200)
            self.send_header("Content-type", 'text/html')
            self.end_headers()

            self.wfile.write('''\
<title>
<head>Error!</head>
</title>

<body>
<h1>Oops!</h1>

<p>
  This server supports HTTP GET requests only for the the purpose of
  obtaining Web Services Description Language (WSDL) for a specific
  service.

  Either you requested an URL that does not end in "wsdl" or this
  server does not implement a wsdl method.
</p>


</body>''')
            
            
    def log_message(self, format, *args):
        if self.server.log:
            BaseHTTPServer.BaseHTTPRequestHandler.\
                log_message (self, format, *args)



class SOAPServer(SocketServer.TCPServer, SOAPServerBase):

    def __init__(self, addr = ('localhost', 8000),
        RequestHandler = SOAPRequestHandler, log = 1, encoding = 'UTF-8',
        config = Config, namespace = None, ssl_context = None):

        # Test the encoding, raising an exception if it's not known
        if encoding != None:
            ''.encode(encoding)

        if ssl_context != None and not config.SSLserver:
            raise AttributeError, \
                "SSL server not supported by this Python installation"

        self.namespace          = namespace
        self.objmap             = {}
        self.funcmap            = {}
        self.ssl_context        = ssl_context
        self.encoding           = encoding
        self.config             = config
        self.log                = log

        self.allow_reuse_address= 1

        SocketServer.TCPServer.__init__(self, addr, RequestHandler)

class ThreadingSOAPServer(SocketServer.ThreadingTCPServer, SOAPServerBase):

    def __init__(self, addr = ('localhost', 8000),
        RequestHandler = SOAPRequestHandler, log = 1, encoding = 'UTF-8',
        config = Config, namespace = None, ssl_context = None):

        # Test the encoding, raising an exception if it's not known
        if encoding != None:
            ''.encode(encoding)

        if ssl_context != None and not config.SSLserver:
            raise AttributeError, \
                "SSL server not supported by this Python installation"

        self.namespace          = namespace
        self.objmap             = {}
        self.funcmap            = {}
        self.ssl_context        = ssl_context
        self.encoding           = encoding
        self.config             = config
        self.log                = log

        self.allow_reuse_address= 1

        SocketServer.ThreadingTCPServer.__init__(self, addr, RequestHandler)

# only define class if Unix domain sockets are available
if hasattr(socket, "AF_UNIX"):

    class SOAPUnixSocketServer(SocketServer.UnixStreamServer, SOAPServerBase):
    
        def __init__(self, addr = 8000,
            RequestHandler = SOAPRequestHandler, log = 1, encoding = 'UTF-8',
            config = Config, namespace = None, ssl_context = None):
    
            # Test the encoding, raising an exception if it's not known
            if encoding != None:
                ''.encode(encoding)
    
            if ssl_context != None and not config.SSLserver:
                raise AttributeError, \
                    "SSL server not supported by this Python installation"
    
            self.namespace          = namespace
            self.objmap             = {}
            self.funcmap            = {}
            self.ssl_context        = ssl_context
            self.encoding           = encoding
            self.config             = config
            self.log                = log
    
            self.allow_reuse_address= 1
    
            SocketServer.UnixStreamServer.__init__(self, str(addr), RequestHandler)
    
