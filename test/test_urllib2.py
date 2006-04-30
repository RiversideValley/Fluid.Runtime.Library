import unittest
from test import test_support

import os, socket
import StringIO

import urllib2
from urllib2 import Request, OpenerDirector

# XXX
# Request
# CacheFTPHandler (hard to write)
# parse_keqv_list, parse_http_list, HTTPDigestAuthHandler

class TrivialTests(unittest.TestCase):
    def test_trivial(self):
        # A couple trivial tests

        self.assertRaises(ValueError, urllib2.urlopen, 'bogus url')

        # XXX Name hacking to get this to work on Windows.
        fname = os.path.abspath(urllib2.__file__).replace('\\', '/')
        if fname[1:2] == ":":
            fname = fname[2:]
        # And more hacking to get it to work on MacOS. This assumes
        # urllib.pathname2url works, unfortunately...
        if os.name == 'mac':
            fname = '/' + fname.replace(':', '/')
        elif os.name == 'riscos':
            import string
            fname = os.expand(fname)
            fname = fname.translate(string.maketrans("/.", "./"))

        file_url = "file://%s" % fname
        f = urllib2.urlopen(file_url)

        buf = f.read()
        f.close()

    def test_parse_http_list(self):
        tests = [('a,b,c', ['a', 'b', 'c']),
                 ('path"o,l"og"i"cal, example', ['path"o,l"og"i"cal', 'example']),
                 ('a, b, "c", "d", "e,f", g, h', ['a', 'b', '"c"', '"d"', '"e,f"', 'g', 'h']),
                 ('a="b\\"c", d="e\\,f", g="h\\\\i"', ['a="b"c"', 'd="e,f"', 'g="h\\i"'])]
        for string, list in tests:
            self.assertEquals(urllib2.parse_http_list(string), list)


def test_password_manager(self):
    """
    >>> mgr = urllib2.HTTPPasswordMgr()
    >>> add = mgr.add_password
    >>> add("Some Realm", "http://example.com/", "joe", "password")
    >>> add("Some Realm", "http://example.com/ni", "ni", "ni")
    >>> add("c", "http://example.com/foo", "foo", "ni")
    >>> add("c", "http://example.com/bar", "bar", "nini")
    >>> add("b", "http://example.com/", "first", "blah")
    >>> add("b", "http://example.com/", "second", "spam")
    >>> add("a", "http://example.com", "1", "a")
    >>> add("Some Realm", "http://c.example.com:3128", "3", "c")
    >>> add("Some Realm", "d.example.com", "4", "d")
    >>> add("Some Realm", "e.example.com:3128", "5", "e")

    >>> mgr.find_user_password("Some Realm", "example.com")
    ('joe', 'password')
    >>> mgr.find_user_password("Some Realm", "http://example.com")
    ('joe', 'password')
    >>> mgr.find_user_password("Some Realm", "http://example.com/")
    ('joe', 'password')
    >>> mgr.find_user_password("Some Realm", "http://example.com/spam")
    ('joe', 'password')
    >>> mgr.find_user_password("Some Realm", "http://example.com/spam/spam")
    ('joe', 'password')
    >>> mgr.find_user_password("c", "http://example.com/foo")
    ('foo', 'ni')
    >>> mgr.find_user_password("c", "http://example.com/bar")
    ('bar', 'nini')

    Currently, we use the highest-level path where more than one match:

    >>> mgr.find_user_password("Some Realm", "http://example.com/ni")
    ('joe', 'password')

    Use latest add_password() in case of conflict:

    >>> mgr.find_user_password("b", "http://example.com/")
    ('second', 'spam')

    No special relationship between a.example.com and example.com:

    >>> mgr.find_user_password("a", "http://example.com/")
    ('1', 'a')
    >>> mgr.find_user_password("a", "http://a.example.com/")
    (None, None)

    Ports:

    >>> mgr.find_user_password("Some Realm", "c.example.com")
    (None, None)
    >>> mgr.find_user_password("Some Realm", "c.example.com:3128")
    ('3', 'c')
    >>> mgr.find_user_password("Some Realm", "http://c.example.com:3128")
    ('3', 'c')
    >>> mgr.find_user_password("Some Realm", "d.example.com")
    ('4', 'd')
    >>> mgr.find_user_password("Some Realm", "e.example.com:3128")
    ('5', 'e')

    """
    pass


class MockOpener:
    addheaders = []
    def open(self, req, data=None):
        self.req, self.data = req, data
    def error(self, proto, *args):
        self.proto, self.args = proto, args

class MockFile:
    def read(self, count=None): pass
    def readline(self, count=None): pass
    def close(self): pass

class MockHeaders(dict):
    def getheaders(self, name):
        return self.values()

class MockResponse(StringIO.StringIO):
    def __init__(self, code, msg, headers, data, url=None):
        StringIO.StringIO.__init__(self, data)
        self.code, self.msg, self.headers, self.url = code, msg, headers, url
    def info(self):
        return self.headers
    def geturl(self):
        return self.url

class MockCookieJar:
    def add_cookie_header(self, request):
        self.ach_req = request
    def extract_cookies(self, response, request):
        self.ec_req, self.ec_r = request, response

class FakeMethod:
    def __init__(self, meth_name, action, handle):
        self.meth_name = meth_name
        self.handle = handle
        self.action = action
    def __call__(self, *args):
        return self.handle(self.meth_name, self.action, *args)

class MockHandler:
    # useful for testing handler machinery
    # see add_ordered_mock_handlers() docstring
    handler_order = 500
    def __init__(self, methods):
        self._define_methods(methods)
    def _define_methods(self, methods):
        for spec in methods:
            if len(spec) == 2: name, action = spec
            else: name, action = spec, None
            meth = FakeMethod(name, action, self.handle)
            setattr(self.__class__, name, meth)
    def handle(self, fn_name, action, *args, **kwds):
        self.parent.calls.append((self, fn_name, args, kwds))
        if action is None:
            return None
        elif action == "return self":
            return self
        elif action == "return response":
            res = MockResponse(200, "OK", {}, "")
            return res
        elif action == "return request":
            return Request("http://blah/")
        elif action.startswith("error"):
            code = action[action.rfind(" ")+1:]
            try:
                code = int(code)
            except ValueError:
                pass
            res = MockResponse(200, "OK", {}, "")
            return self.parent.error("http", args[0], res, code, "", {})
        elif action == "raise":
            raise urllib2.URLError("blah")
        assert False
    def close(self): pass
    def add_parent(self, parent):
        self.parent = parent
        self.parent.calls = []
    def __lt__(self, other):
        if not hasattr(other, "handler_order"):
            # No handler_order, leave in original order.  Yuck.
            return True
        return self.handler_order < other.handler_order

def add_ordered_mock_handlers(opener, meth_spec):
    """Create MockHandlers and add them to an OpenerDirector.

    meth_spec: list of lists of tuples and strings defining methods to define
    on handlers.  eg:

    [["http_error", "ftp_open"], ["http_open"]]

    defines methods .http_error() and .ftp_open() on one handler, and
    .http_open() on another.  These methods just record their arguments and
    return None.  Using a tuple instead of a string causes the method to
    perform some action (see MockHandler.handle()), eg:

    [["http_error"], [("http_open", "return request")]]

    defines .http_error() on one handler (which simply returns None), and
    .http_open() on another handler, which returns a Request object.

    """
    handlers = []
    count = 0
    for meths in meth_spec:
        class MockHandlerSubclass(MockHandler): pass
        h = MockHandlerSubclass(meths)
        h.handler_order += count
        h.add_parent(opener)
        count = count + 1
        handlers.append(h)
        opener.add_handler(h)
    return handlers

def build_test_opener(*handler_instances):
    opener = OpenerDirector()
    for h in handler_instances:
        opener.add_handler(h)
    return opener

class MockHTTPHandler(urllib2.BaseHandler):
    # useful for testing redirections and auth
    # sends supplied headers and code as first response
    # sends 200 OK as second response
    def __init__(self, code, headers):
        self.code = code
        self.headers = headers
        self.reset()
    def reset(self):
        self._count = 0
        self.requests = []
    def http_open(self, req):
        import mimetools, httplib, copy
        from StringIO import StringIO
        self.requests.append(copy.deepcopy(req))
        if self._count == 0:
            self._count = self._count + 1
            name = httplib.responses[self.code]
            msg = mimetools.Message(StringIO(self.headers))
            return self.parent.error(
                "http", req, MockFile(), self.code, name, msg)
        else:
            self.req = req
            msg = mimetools.Message(StringIO("\r\n\r\n"))
            return MockResponse(200, "OK", msg, "", req.get_full_url())

class MockPasswordManager:
    def add_password(self, realm, uri, user, password):
        self.realm = realm
        self.url = uri
        self.user = user
        self.password = password
    def find_user_password(self, realm, authuri):
        self.target_realm = realm
        self.target_url = authuri
        return self.user, self.password


class OpenerDirectorTests(unittest.TestCase):

    def test_handled(self):
        # handler returning non-None means no more handlers will be called
        o = OpenerDirector()
        meth_spec = [
            ["http_open", "ftp_open", "http_error_302"],
            ["ftp_open"],
            [("http_open", "return self")],
            [("http_open", "return self")],
            ]
        handlers = add_ordered_mock_handlers(o, meth_spec)

        req = Request("http://example.com/")
        r = o.open(req)
        # Second .http_open() gets called, third doesn't, since second returned
        # non-None.  Handlers without .http_open() never get any methods called
        # on them.
        # In fact, second mock handler defining .http_open() returns self
        # (instead of response), which becomes the OpenerDirector's return
        # value.
        self.assertEqual(r, handlers[2])
        calls = [(handlers[0], "http_open"), (handlers[2], "http_open")]
        for expected, got in zip(calls, o.calls):
            handler, name, args, kwds = got
            self.assertEqual((handler, name), expected)
            self.assertEqual(args, (req,))

    def test_handler_order(self):
        o = OpenerDirector()
        handlers = []
        for meths, handler_order in [
            ([("http_open", "return self")], 500),
            (["http_open"], 0),
            ]:
            class MockHandlerSubclass(MockHandler): pass
            h = MockHandlerSubclass(meths)
            h.handler_order = handler_order
            handlers.append(h)
            o.add_handler(h)

        r = o.open("http://example.com/")
        # handlers called in reverse order, thanks to their sort order
        self.assertEqual(o.calls[0][0], handlers[1])
        self.assertEqual(o.calls[1][0], handlers[0])

    def test_raise(self):
        # raising URLError stops processing of request
        o = OpenerDirector()
        meth_spec = [
            [("http_open", "raise")],
            [("http_open", "return self")],
            ]
        handlers = add_ordered_mock_handlers(o, meth_spec)

        req = Request("http://example.com/")
        self.assertRaises(urllib2.URLError, o.open, req)
        self.assertEqual(o.calls, [(handlers[0], "http_open", (req,), {})])

##     def test_error(self):
##         # XXX this doesn't actually seem to be used in standard library,
##         #  but should really be tested anyway...

    def test_http_error(self):
        # XXX http_error_default
        # http errors are a special case
        o = OpenerDirector()
        meth_spec = [
            [("http_open", "error 302")],
            [("http_error_400", "raise"), "http_open"],
            [("http_error_302", "return response"), "http_error_303",
             "http_error"],
            [("http_error_302")],
            ]
        handlers = add_ordered_mock_handlers(o, meth_spec)

        class Unknown:
            def __eq__(self, other): return True

        req = Request("http://example.com/")
        r = o.open(req)
        assert len(o.calls) == 2
        calls = [(handlers[0], "http_open", (req,)),
                 (handlers[2], "http_error_302",
                  (req, Unknown(), 302, "", {}))]
        for expected, got in zip(calls, o.calls):
            handler, method_name, args = expected
            self.assertEqual((handler, method_name), got[:2])
            self.assertEqual(args, got[2])

    def test_processors(self):
        # *_request / *_response methods get called appropriately
        o = OpenerDirector()
        meth_spec = [
            [("http_request", "return request"),
             ("http_response", "return response")],
            [("http_request", "return request"),
             ("http_response", "return response")],
            ]
        handlers = add_ordered_mock_handlers(o, meth_spec)

        req = Request("http://example.com/")
        r = o.open(req)
        # processor methods are called on *all* handlers that define them,
        # not just the first handler that handles the request
        calls = [
            (handlers[0], "http_request"), (handlers[1], "http_request"),
            (handlers[0], "http_response"), (handlers[1], "http_response")]

        for i, (handler, name, args, kwds) in enumerate(o.calls):
            if i < 2:
                # *_request
                self.assertEqual((handler, name), calls[i])
                self.assertEqual(len(args), 1)
                self.assert_(isinstance(args[0], Request))
            else:
                # *_response
                self.assertEqual((handler, name), calls[i])
                self.assertEqual(len(args), 2)
                self.assert_(isinstance(args[0], Request))
                # response from opener.open is None, because there's no
                # handler that defines http_open to handle it
                self.assert_(args[1] is None or
                             isinstance(args[1], MockResponse))


def sanepathname2url(path):
    import urllib
    urlpath = urllib.pathname2url(path)
    if os.name == "nt" and urlpath.startswith("///"):
        urlpath = urlpath[2:]
    # XXX don't ask me about the mac...
    return urlpath

class HandlerTests(unittest.TestCase):

    def test_ftp(self):
        class MockFTPWrapper:
            def __init__(self, data): self.data = data
            def retrfile(self, filename, filetype):
                self.filename, self.filetype = filename, filetype
                return StringIO.StringIO(self.data), len(self.data)

        class NullFTPHandler(urllib2.FTPHandler):
            def __init__(self, data): self.data = data
            def connect_ftp(self, user, passwd, host, port, dirs):
                self.user, self.passwd = user, passwd
                self.host, self.port = host, port
                self.dirs = dirs
                self.ftpwrapper = MockFTPWrapper(self.data)
                return self.ftpwrapper

        import ftplib, socket
        data = "rheum rhaponicum"
        h = NullFTPHandler(data)
        o = h.parent = MockOpener()

        for url, host, port, type_, dirs, filename, mimetype in [
            ("ftp://localhost/foo/bar/baz.html",
             "localhost", ftplib.FTP_PORT, "I",
             ["foo", "bar"], "baz.html", "text/html"),
            ("ftp://localhost:80/foo/bar/",
             "localhost", 80, "D",
             ["foo", "bar"], "", None),
            ("ftp://localhost/baz.gif;type=a",
             "localhost", ftplib.FTP_PORT, "A",
             [], "baz.gif", None),  # XXX really this should guess image/gif
            ]:
            r = h.ftp_open(Request(url))
            # ftp authentication not yet implemented by FTPHandler
            self.assert_(h.user == h.passwd == "")
            self.assertEqual(h.host, socket.gethostbyname(host))
            self.assertEqual(h.port, port)
            self.assertEqual(h.dirs, dirs)
            self.assertEqual(h.ftpwrapper.filename, filename)
            self.assertEqual(h.ftpwrapper.filetype, type_)
            headers = r.info()
            self.assertEqual(headers.get("Content-type"), mimetype)
            self.assertEqual(int(headers["Content-length"]), len(data))

    def test_file(self):
        import time, rfc822, socket
        h = urllib2.FileHandler()
        o = h.parent = MockOpener()

        TESTFN = test_support.TESTFN
        urlpath = sanepathname2url(os.path.abspath(TESTFN))
        towrite = "hello, world\n"
        urls = [
            "file://localhost%s" % urlpath,
            "file://%s" % urlpath,
            "file://%s%s" % (socket.gethostbyname('localhost'), urlpath),
            ]
        try:
            localaddr = socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            localaddr = ''
        if localaddr:
            urls.append("file://%s%s" % (localaddr, urlpath))

        for url in urls:
            f = open(TESTFN, "wb")
            try:
                try:
                    f.write(towrite)
                finally:
                    f.close()

                r = h.file_open(Request(url))
                try:
                    data = r.read()
                    headers = r.info()
                    newurl = r.geturl()
                finally:
                    r.close()
                stats = os.stat(TESTFN)
                modified = rfc822.formatdate(stats.st_mtime)
            finally:
                os.remove(TESTFN)
            self.assertEqual(data, towrite)
            self.assertEqual(headers["Content-type"], "text/plain")
            self.assertEqual(headers["Content-length"], "13")
            self.assertEqual(headers["Last-modified"], modified)

        for url in [
            "file://localhost:80%s" % urlpath,
# XXXX bug: these fail with socket.gaierror, should be URLError
##             "file://%s:80%s/%s" % (socket.gethostbyname('localhost'),
##                                    os.getcwd(), TESTFN),
##             "file://somerandomhost.ontheinternet.com%s/%s" %
##             (os.getcwd(), TESTFN),
            ]:
            try:
                f = open(TESTFN, "wb")
                try:
                    f.write(towrite)
                finally:
                    f.close()

                self.assertRaises(urllib2.URLError,
                                  h.file_open, Request(url))
            finally:
                os.remove(TESTFN)

        h = urllib2.FileHandler()
        o = h.parent = MockOpener()
        # XXXX why does // mean ftp (and /// mean not ftp!), and where
        #  is file: scheme specified?  I think this is really a bug, and
        #  what was intended was to distinguish between URLs like:
        # file:/blah.txt (a file)
        # file://localhost/blah.txt (a file)
        # file:///blah.txt (a file)
        # file://ftp.example.com/blah.txt (an ftp URL)
        for url, ftp in [
            ("file://ftp.example.com//foo.txt", True),
            ("file://ftp.example.com///foo.txt", False),
# XXXX bug: fails with OSError, should be URLError
            ("file://ftp.example.com/foo.txt", False),
            ]:
            req = Request(url)
            try:
                h.file_open(req)
            # XXXX remove OSError when bug fixed
            except (urllib2.URLError, OSError):
                self.assert_(not ftp)
            else:
                self.assert_(o.req is req)
                self.assertEqual(req.type, "ftp")

    def test_http(self):
        class MockHTTPResponse:
            def __init__(self, fp, msg, status, reason):
                self.fp = fp
                self.msg = msg
                self.status = status
                self.reason = reason
            def read(self):
                return ''
        class MockHTTPClass:
            def __init__(self):
                self.req_headers = []
                self.data = None
                self.raise_on_endheaders = False
            def __call__(self, host):
                self.host = host
                return self
            def set_debuglevel(self, level):
                self.level = level
            def request(self, method, url, body=None, headers={}):
                self.method = method
                self.selector = url
                self.req_headers += headers.items()
                if body:
                    self.data = body
                if self.raise_on_endheaders:
                    import socket
                    raise socket.error()
            def getresponse(self):
                return MockHTTPResponse(MockFile(), {}, 200, "OK")

        h = urllib2.AbstractHTTPHandler()
        o = h.parent = MockOpener()

        url = "http://example.com/"
        for method, data in [("GET", None), ("POST", "blah")]:
            req = Request(url, data, {"Foo": "bar"})
            req.add_unredirected_header("Spam", "eggs")
            http = MockHTTPClass()
            r = h.do_open(http, req)

            # result attributes
            r.read; r.readline  # wrapped MockFile methods
            r.info; r.geturl  # addinfourl methods
            r.code, r.msg == 200, "OK"  # added from MockHTTPClass.getreply()
            hdrs = r.info()
            hdrs.get; hdrs.has_key  # r.info() gives dict from .getreply()
            self.assertEqual(r.geturl(), url)

            self.assertEqual(http.host, "example.com")
            self.assertEqual(http.level, 0)
            self.assertEqual(http.method, method)
            self.assertEqual(http.selector, "/")
            self.assertEqual(http.req_headers,
                             [("Connection", "close"),
                              ("Foo", "bar"), ("Spam", "eggs")])
            self.assertEqual(http.data, data)

        # check socket.error converted to URLError
        http.raise_on_endheaders = True
        self.assertRaises(urllib2.URLError, h.do_open, http, req)

        # check adding of standard headers
        o.addheaders = [("Spam", "eggs")]
        for data in "", None:  # POST, GET
            req = Request("http://example.com/", data)
            r = MockResponse(200, "OK", {}, "")
            newreq = h.do_request_(req)
            if data is None:  # GET
                self.assert_("Content-length" not in req.unredirected_hdrs)
                self.assert_("Content-type" not in req.unredirected_hdrs)
            else:  # POST
                self.assertEqual(req.unredirected_hdrs["Content-length"], "0")
                self.assertEqual(req.unredirected_hdrs["Content-type"],
                             "application/x-www-form-urlencoded")
            # XXX the details of Host could be better tested
            self.assertEqual(req.unredirected_hdrs["Host"], "example.com")
            self.assertEqual(req.unredirected_hdrs["Spam"], "eggs")

            # don't clobber existing headers
            req.add_unredirected_header("Content-length", "foo")
            req.add_unredirected_header("Content-type", "bar")
            req.add_unredirected_header("Host", "baz")
            req.add_unredirected_header("Spam", "foo")
            newreq = h.do_request_(req)
            self.assertEqual(req.unredirected_hdrs["Content-length"], "foo")
            self.assertEqual(req.unredirected_hdrs["Content-type"], "bar")
            self.assertEqual(req.unredirected_hdrs["Host"], "baz")
            self.assertEqual(req.unredirected_hdrs["Spam"], "foo")

    def test_errors(self):
        h = urllib2.HTTPErrorProcessor()
        o = h.parent = MockOpener()

        url = "http://example.com/"
        req = Request(url)
        # 200 OK is passed through
        r = MockResponse(200, "OK", {}, "", url)
        newr = h.http_response(req, r)
        self.assert_(r is newr)
        self.assert_(not hasattr(o, "proto"))  # o.error not called
        # anything else calls o.error (and MockOpener returns None, here)
        r = MockResponse(201, "Created", {}, "", url)
        self.assert_(h.http_response(req, r) is None)
        self.assertEqual(o.proto, "http")  # o.error called
        self.assertEqual(o.args, (req, r, 201, "Created", {}))

    def test_cookies(self):
        cj = MockCookieJar()
        h = urllib2.HTTPCookieProcessor(cj)
        o = h.parent = MockOpener()

        req = Request("http://example.com/")
        r = MockResponse(200, "OK", {}, "")
        newreq = h.http_request(req)
        self.assert_(cj.ach_req is req is newreq)
        self.assertEquals(req.get_origin_req_host(), "example.com")
        self.assert_(not req.is_unverifiable())
        newr = h.http_response(req, r)
        self.assert_(cj.ec_req is req)
        self.assert_(cj.ec_r is r is newr)

    def test_redirect(self):
        from_url = "http://example.com/a.html"
        to_url = "http://example.com/b.html"
        h = urllib2.HTTPRedirectHandler()
        o = h.parent = MockOpener()

        # ordinary redirect behaviour
        for code in 301, 302, 303, 307:
            for data in None, "blah\nblah\n":
                method = getattr(h, "http_error_%s" % code)
                req = Request(from_url, data)
                req.add_header("Nonsense", "viking=withhold")
                req.add_unredirected_header("Spam", "spam")
                try:
                    method(req, MockFile(), code, "Blah",
                           MockHeaders({"location": to_url}))
                except urllib2.HTTPError:
                    # 307 in response to POST requires user OK
                    self.assert_(code == 307 and data is not None)
                self.assertEqual(o.req.get_full_url(), to_url)
                try:
                    self.assertEqual(o.req.get_method(), "GET")
                except AttributeError:
                    self.assert_(not o.req.has_data())
                self.assertEqual(o.req.headers["Nonsense"],
                                 "viking=withhold")
                self.assert_("Spam" not in o.req.headers)
                self.assert_("Spam" not in o.req.unredirected_hdrs)

        # loop detection
        req = Request(from_url)
        def redirect(h, req, url=to_url):
            h.http_error_302(req, MockFile(), 302, "Blah",
                             MockHeaders({"location": url}))
        # Note that the *original* request shares the same record of
        # redirections with the sub-requests caused by the redirections.

        # detect infinite loop redirect of a URL to itself
        req = Request(from_url, origin_req_host="example.com")
        count = 0
        try:
            while 1:
                redirect(h, req, "http://example.com/")
                count = count + 1
        except urllib2.HTTPError:
            # don't stop until max_repeats, because cookies may introduce state
            self.assertEqual(count, urllib2.HTTPRedirectHandler.max_repeats)

        # detect endless non-repeating chain of redirects
        req = Request(from_url, origin_req_host="example.com")
        count = 0
        try:
            while 1:
                redirect(h, req, "http://example.com/%d" % count)
                count = count + 1
        except urllib2.HTTPError:
            self.assertEqual(count,
                             urllib2.HTTPRedirectHandler.max_redirections)

    def test_cookie_redirect(self):
        # cookies shouldn't leak into redirected requests
        from cookielib import CookieJar

        from test.test_cookielib import interact_netscape

        cj = CookieJar()
        interact_netscape(cj, "http://www.example.com/", "spam=eggs")
        hh = MockHTTPHandler(302, "Location: http://www.cracker.com/\r\n\r\n")
        hdeh = urllib2.HTTPDefaultErrorHandler()
        hrh = urllib2.HTTPRedirectHandler()
        cp = urllib2.HTTPCookieProcessor(cj)
        o = build_test_opener(hh, hdeh, hrh, cp)
        o.open("http://www.example.com/")
        self.assert_(not hh.req.has_header("Cookie"))

    def test_proxy(self):
        o = OpenerDirector()
        ph = urllib2.ProxyHandler(dict(http="proxy.example.com:3128"))
        o.add_handler(ph)
        meth_spec = [
            [("http_open", "return response")]
            ]
        handlers = add_ordered_mock_handlers(o, meth_spec)

        req = Request("http://acme.example.com/")
        self.assertEqual(req.get_host(), "acme.example.com")
        r = o.open(req)
        self.assertEqual(req.get_host(), "proxy.example.com:3128")

        self.assertEqual([(handlers[0], "http_open")],
                         [tup[0:2] for tup in o.calls])

    def test_basic_auth(self):
        opener = OpenerDirector()
        password_manager = MockPasswordManager()
        auth_handler = urllib2.HTTPBasicAuthHandler(password_manager)
        realm = "ACME Widget Store"
        http_handler = MockHTTPHandler(
            401, 'WWW-Authenticate: Basic realm="%s"\r\n\r\n' % realm)
        self._test_basic_auth(opener, auth_handler, "Authorization",
                              realm, http_handler, password_manager,
                              "http://acme.example.com/protected",
                              "http://acme.example.com/protected",
                              )

    def test_proxy_basic_auth(self):
        opener = OpenerDirector()
        ph = urllib2.ProxyHandler(dict(http="proxy.example.com:3128"))
        opener.add_handler(ph)
        password_manager = MockPasswordManager()
        auth_handler = urllib2.ProxyBasicAuthHandler(password_manager)
        realm = "ACME Networks"
        http_handler = MockHTTPHandler(
            407, 'Proxy-Authenticate: Basic realm="%s"\r\n\r\n' % realm)
        self._test_basic_auth(opener, auth_handler, "Proxy-authorization",
                              realm, http_handler, password_manager,
                              "http://acme.example.com:3128/protected",
                              "proxy.example.com:3128",
                              )

    def _test_basic_auth(self, opener, auth_handler, auth_header,
                         realm, http_handler, password_manager,
                         request_url, protected_url):
        import base64, httplib
        user, password = "wile", "coyote"
        opener.add_handler(auth_handler)
        opener.add_handler(http_handler)

        # .add_password() fed through to password manager
        auth_handler.add_password(realm, request_url, user, password)
        self.assertEqual(realm, password_manager.realm)
        self.assertEqual(request_url, password_manager.url)
        self.assertEqual(user, password_manager.user)
        self.assertEqual(password, password_manager.password)

        r = opener.open(request_url)

        # should have asked the password manager for the username/password
        self.assertEqual(password_manager.target_realm, realm)
        self.assertEqual(password_manager.target_url, protected_url)

        # expect one request without authorization, then one with
        self.assertEqual(len(http_handler.requests), 2)
        self.assertFalse(http_handler.requests[0].has_header(auth_header))
        userpass = '%s:%s' % (user, password)
        auth_hdr_value = 'Basic '+base64.encodestring(userpass).strip()
        self.assertEqual(http_handler.requests[1].get_header(auth_header),
                         auth_hdr_value)

        # if the password manager can't find a password, the handler won't
        # handle the HTTP auth error
        password_manager.user = password_manager.password = None
        http_handler.reset()
        r = opener.open(request_url)
        self.assertEqual(len(http_handler.requests), 1)
        self.assertFalse(http_handler.requests[0].has_header(auth_header))


class MiscTests(unittest.TestCase):

    def test_build_opener(self):
        class MyHTTPHandler(urllib2.HTTPHandler): pass
        class FooHandler(urllib2.BaseHandler):
            def foo_open(self): pass
        class BarHandler(urllib2.BaseHandler):
            def bar_open(self): pass

        build_opener = urllib2.build_opener

        o = build_opener(FooHandler, BarHandler)
        self.opener_has_handler(o, FooHandler)
        self.opener_has_handler(o, BarHandler)

        # can take a mix of classes and instances
        o = build_opener(FooHandler, BarHandler())
        self.opener_has_handler(o, FooHandler)
        self.opener_has_handler(o, BarHandler)

        # subclasses of default handlers override default handlers
        o = build_opener(MyHTTPHandler)
        self.opener_has_handler(o, MyHTTPHandler)

        # a particular case of overriding: default handlers can be passed
        # in explicitly
        o = build_opener()
        self.opener_has_handler(o, urllib2.HTTPHandler)
        o = build_opener(urllib2.HTTPHandler)
        self.opener_has_handler(o, urllib2.HTTPHandler)
        o = build_opener(urllib2.HTTPHandler())
        self.opener_has_handler(o, urllib2.HTTPHandler)

    def opener_has_handler(self, opener, handler_class):
        for h in opener.handlers:
            if h.__class__ == handler_class:
                break
        else:
            self.assert_(False)

class NetworkTests(unittest.TestCase):
    def setUp(self):
        if 0:  # for debugging
            import logging
            logger = logging.getLogger("test_urllib2")
            logger.addHandler(logging.StreamHandler())

    def test_range (self):
        req = urllib2.Request("http://www.python.org",
                              headers={'Range': 'bytes=20-39'})
        result = urllib2.urlopen(req)
        data = result.read()
        self.assertEqual(len(data), 20)

    # XXX The rest of these tests aren't very good -- they don't check much.
    # They do sometimes catch some major disasters, though.

    def test_ftp(self):
        urls = [
            'ftp://www.python.org/pub/python/misc/sousa.au',
            'ftp://www.python.org/pub/tmp/blat',
            'ftp://gatekeeper.research.compaq.com/pub/DEC/SRC'
                '/research-reports/00README-Legal-Rules-Regs',
            ]
        self._test_urls(urls, self._extra_handlers())

    def test_gopher(self):
        import warnings
        warnings.filterwarnings("ignore",
                                "the gopherlib module is deprecated",
                                DeprecationWarning,
                                "urllib2$")
        urls = [
            # Thanks to Fred for finding these!
            'gopher://gopher.lib.ncsu.edu/11/library/stacks/Alex',
            'gopher://gopher.vt.edu:10010/10/33',
            ]
        self._test_urls(urls, self._extra_handlers())

    def test_file(self):
        TESTFN = test_support.TESTFN
        f = open(TESTFN, 'w')
        try:
            f.write('hi there\n')
            f.close()
            urls = [
                'file:'+sanepathname2url(os.path.abspath(TESTFN)),

                # XXX bug, should raise URLError
                #('file://nonsensename/etc/passwd', None, urllib2.URLError)
                ('file://nonsensename/etc/passwd', None, (OSError, socket.error))
                ]
            self._test_urls(urls, self._extra_handlers())
        finally:
            os.remove(TESTFN)

    def test_http(self):
        urls = [
            'http://www.espn.com/', # redirect
            'http://www.python.org/Spanish/Inquistion/',
            ('http://www.python.org/cgi-bin/faqw.py',
             'query=pythonistas&querytype=simple&casefold=yes&req=search', None),
            'http://www.python.org/',
            ]
        self._test_urls(urls, self._extra_handlers())

    # XXX Following test depends on machine configurations that are internal
    # to CNRI.  Need to set up a public server with the right authentication
    # configuration for test purposes.

##     def test_cnri(self):
##         if socket.gethostname() == 'bitdiddle':
##             localhost = 'bitdiddle.cnri.reston.va.us'
##         elif socket.gethostname() == 'bitdiddle.concentric.net':
##             localhost = 'localhost'
##         else:
##             localhost = None
##         if localhost is not None:
##             urls = [
##                 'file://%s/etc/passwd' % localhost,
##                 'http://%s/simple/' % localhost,
##                 'http://%s/digest/' % localhost,
##                 'http://%s/not/found.h' % localhost,
##                 ]

##             bauth = HTTPBasicAuthHandler()
##             bauth.add_password('basic_test_realm', localhost, 'jhylton',
##                                'password')
##             dauth = HTTPDigestAuthHandler()
##             dauth.add_password('digest_test_realm', localhost, 'jhylton',
##                                'password')

##             self._test_urls(urls, self._extra_handlers()+[bauth, dauth])

    def _test_urls(self, urls, handlers):
        import socket
        import time
        import logging
        debug = logging.getLogger("test_urllib2").debug

        urllib2.install_opener(urllib2.build_opener(*handlers))

        for url in urls:
            if isinstance(url, tuple):
                url, req, expected_err = url
            else:
                req = expected_err = None
            debug(url)
            try:
                f = urllib2.urlopen(url, req)
            except (IOError, socket.error, OSError), err:
                debug(err)
                if expected_err:
                    self.assert_(isinstance(err, expected_err))
            else:
                buf = f.read()
                f.close()
                debug("read %d bytes" % len(buf))
            debug("******** next url coming up...")
            time.sleep(0.1)

    def _extra_handlers(self):
        handlers = []

        handlers.append(urllib2.GopherHandler)

        cfh = urllib2.CacheFTPHandler()
        cfh.setTimeout(1)
        handlers.append(cfh)

        return handlers


def test_main(verbose=None):
    from test import test_urllib2
    test_support.run_doctest(test_urllib2, verbose)
    test_support.run_doctest(urllib2, verbose)
    tests = (TrivialTests,
             OpenerDirectorTests,
             HandlerTests,
             MiscTests)
    if test_support.is_resource_enabled('network'):
        tests += (NetworkTests,)
    test_support.run_unittest(*tests)

if __name__ == "__main__":
    test_main(verbose=True)
