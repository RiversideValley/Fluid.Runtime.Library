import socket
import threading
import telnetlib
import time
import queue

from unittest import TestCase
from test import support

HOST = support.HOST
EOF_sigil = object()

def server(evt, serv, dataq=None):
    """ Open a tcp server in three steps
        1) set evt to true to let the parent know we are ready
        2) [optional] if is not False, write the list of data from dataq.get()
           to the socket.
        3) set evt to true to let the parent know we're done
    """
    serv.listen(5)
    evt.set()
    try:
        conn, addr = serv.accept()
        if dataq:
            data = b''
            new_data = dataq.get(True, 0.5)
            dataq.task_done()
            for item in new_data:
                if item == EOF_sigil:
                    break
                if type(item) in [int, float]:
                    time.sleep(item)
                else:
                    data += item
                written = conn.send(data)
                data = data[written:]
    except socket.timeout:
        pass
    finally:
        serv.close()
        evt.set()

class GeneralTests(TestCase):

    def setUp(self):
        self.evt = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(3)
        self.port = support.bind_port(self.sock)
        self.thread = threading.Thread(target=server, args=(self.evt,self.sock))
        self.thread.start()
        self.evt.wait()
        self.evt.clear()
        time.sleep(.1)

    def tearDown(self):
        self.evt.wait()
        self.thread.join()

    def testBasic(self):
        # connects
        telnet = telnetlib.Telnet(HOST, self.port)
        telnet.sock.close()

    def testTimeoutDefault(self):
        self.assertTrue(socket.getdefaulttimeout() is None)
        socket.setdefaulttimeout(30)
        try:
            telnet = telnetlib.Telnet("localhost", self.port)
        finally:
            socket.setdefaulttimeout(None)
        self.assertEqual(telnet.sock.gettimeout(), 30)
        telnet.sock.close()

    def testTimeoutNone(self):
        # None, having other default
        self.assertTrue(socket.getdefaulttimeout() is None)
        socket.setdefaulttimeout(30)
        try:
            telnet = telnetlib.Telnet(HOST, self.port, timeout=None)
        finally:
            socket.setdefaulttimeout(None)
        self.assertTrue(telnet.sock.gettimeout() is None)
        telnet.sock.close()

    def testTimeoutValue(self):
        telnet = telnetlib.Telnet("localhost", self.port, timeout=30)
        self.assertEqual(telnet.sock.gettimeout(), 30)
        telnet.sock.close()

    def testTimeoutOpen(self):
        telnet = telnetlib.Telnet()
        telnet.open("localhost", self.port, timeout=30)
        self.assertEqual(telnet.sock.gettimeout(), 30)
        telnet.sock.close()

def _read_setUp(self):
    self.evt = threading.Event()
    self.dataq = queue.Queue()
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.settimeout(3)
    self.port = support.bind_port(self.sock)
    self.thread = threading.Thread(target=server, args=(self.evt,self.sock, self.dataq))
    self.thread.start()
    self.evt.wait()
    self.evt.clear()
    time.sleep(.1)

def _read_tearDown(self):
    self.evt.wait()
    self.thread.join()

class ReadTests(TestCase):
    setUp = _read_setUp
    tearDown = _read_tearDown

    # use a similar approach to testing timeouts as test_timeout.py
    # these will never pass 100% but make the fuzz big enough that it is rare
    block_long = 0.6
    block_short = 0.3
    def test_read_until_A(self):
        """
        read_until(expected, [timeout])
          Read until the expected string has been seen, or a timeout is
          hit (default is no timeout); may block.
        """
        want = [b'x' * 10, b'match', b'y' * 10, EOF_sigil]
        self.dataq.put(want)
        telnet = telnetlib.Telnet(HOST, self.port)
        self.dataq.join()
        data = telnet.read_until(b'match')
        self.assertEqual(data, b''.join(want[:-2]))

    def test_read_until_B(self):
        # test the timeout - it does NOT raise socket.timeout
        want = [b'hello', self.block_long, b'not seen', EOF_sigil]
        self.dataq.put(want)
        telnet = telnetlib.Telnet(HOST, self.port)
        self.dataq.join()
        data = telnet.read_until(b'not seen', self.block_short)
        self.assertEqual(data, want[0])
        self.assertEqual(telnet.read_all(), b'not seen')

    def test_read_all_A(self):
        """
        read_all()
          Read all data until EOF; may block.
        """
        want = [b'x' * 500, b'y' * 500, b'z' * 500, EOF_sigil]
        self.dataq.put(want)
        telnet = telnetlib.Telnet(HOST, self.port)
        self.dataq.join()
        data = telnet.read_all()
        self.assertEqual(data, b''.join(want[:-1]))
        return

    def _test_blocking(self, func):
        self.dataq.put([self.block_long, EOF_sigil])
        self.dataq.join()
        start = time.time()
        data = func()
        self.assertTrue(self.block_short <= time.time() - start)

    def test_read_all_B(self):
        self._test_blocking(telnetlib.Telnet(HOST, self.port).read_all)

    def test_read_all_C(self):
        self.dataq.put([EOF_sigil])
        telnet = telnetlib.Telnet(HOST, self.port)
        self.dataq.join()
        telnet.read_all()
        telnet.read_all() # shouldn't raise

    def test_read_some_A(self):
        """
        read_some()
          Read at least one byte or EOF; may block.
        """
        # test 'at least one byte'
        want = [b'x' * 500, EOF_sigil]
        self.dataq.put(want)
        telnet = telnetlib.Telnet(HOST, self.port)
        self.dataq.join()
        data = telnet.read_all()
        self.assertTrue(len(data) >= 1)

    def test_read_some_B(self):
        # test EOF
        self.dataq.put([EOF_sigil])
        telnet = telnetlib.Telnet(HOST, self.port)
        self.dataq.join()
        self.assertEqual(b'', telnet.read_some())

    def test_read_some_C(self):
        self._test_blocking(telnetlib.Telnet(HOST, self.port).read_some)

    def _test_read_any_eager_A(self, func_name):
        """
        read_very_eager()
          Read all data available already queued or on the socket,
          without blocking.
        """
        want = [self.block_long, b'x' * 100, b'y' * 100, EOF_sigil]
        expects = want[1] + want[2]
        self.dataq.put(want)
        telnet = telnetlib.Telnet(HOST, self.port)
        self.dataq.join()
        func = getattr(telnet, func_name)
        data = b''
        while True:
            try:
                data += func()
                self.assertTrue(expects.startswith(data))
            except EOFError:
                break
        self.assertEqual(expects, data)

    def _test_read_any_eager_B(self, func_name):
        # test EOF
        self.dataq.put([EOF_sigil])
        telnet = telnetlib.Telnet(HOST, self.port)
        self.dataq.join()
        time.sleep(self.block_short)
        func = getattr(telnet, func_name)
        self.assertRaises(EOFError, func)

    # read_eager and read_very_eager make the same gaurantees
    # (they behave differently but we only test the gaurantees)
    def test_read_very_eager_A(self):
        self._test_read_any_eager_A('read_very_eager')
    def test_read_very_eager_B(self):
        self._test_read_any_eager_B('read_very_eager')
    def test_read_eager_A(self):
        self._test_read_any_eager_A('read_eager')
    def test_read_eager_B(self):
        self._test_read_any_eager_B('read_eager')
    # NB -- we need to test the IAC block which is mentioned in the docstring
    # but not in the module docs

    def _test_read_any_lazy_B(self, func_name):
        self.dataq.put([EOF_sigil])
        telnet = telnetlib.Telnet(HOST, self.port)
        self.dataq.join()
        func = getattr(telnet, func_name)
        telnet.fill_rawq()
        self.assertRaises(EOFError, func)

    def test_read_lazy_A(self):
        want = [b'x' * 100, EOF_sigil]
        self.dataq.put(want)
        telnet = telnetlib.Telnet(HOST, self.port)
        self.dataq.join()
        time.sleep(self.block_short)
        self.assertEqual(b'', telnet.read_lazy())
        data = b''
        while True:
            try:
                read_data = telnet.read_lazy()
                data += read_data
                if not read_data:
                    telnet.fill_rawq()
            except EOFError:
                break
            self.assertTrue(want[0].startswith(data))
        self.assertEqual(data, want[0])

    def test_read_lazy_B(self):
        self._test_read_any_lazy_B('read_lazy')

    def test_read_very_lazy_A(self):
        want = [b'x' * 100, EOF_sigil]
        self.dataq.put(want)
        telnet = telnetlib.Telnet(HOST, self.port)
        self.dataq.join()
        time.sleep(self.block_short)
        self.assertEqual(b'', telnet.read_very_lazy())
        data = b''
        while True:
            try:
                read_data = telnet.read_very_lazy()
            except EOFError:
                break
            data += read_data
            if not read_data:
                telnet.fill_rawq()
                self.assertEqual(b'', telnet.cookedq)
                telnet.process_rawq()
            self.assertTrue(want[0].startswith(data))
        self.assertEqual(data, want[0])

    def test_read_very_lazy_B(self):
        self._test_read_any_lazy_B('read_very_lazy')

class nego_collector(object):
    def __init__(self, sb_getter=None):
        self.seen = b''
        self.sb_getter = sb_getter
        self.sb_seen = b''

    def do_nego(self, sock, cmd, opt):
        self.seen += cmd + opt
        if cmd == tl.SE and self.sb_getter:
            sb_data = self.sb_getter()
            self.sb_seen += sb_data

tl = telnetlib
class OptionTests(TestCase):
    setUp = _read_setUp
    tearDown = _read_tearDown
    # RFC 854 commands
    cmds = [tl.AO, tl.AYT, tl.BRK, tl.EC, tl.EL, tl.GA, tl.IP, tl.NOP]

    def _test_command(self, data):
        """ helper for testing IAC + cmd """
        self.setUp()
        self.dataq.put(data)
        telnet = telnetlib.Telnet(HOST, self.port)
        self.dataq.join()
        nego = nego_collector()
        telnet.set_option_negotiation_callback(nego.do_nego)
        txt = telnet.read_all()
        cmd = nego.seen
        self.assertTrue(len(cmd) > 0) # we expect at least one command
        self.assertTrue(cmd[:1] in self.cmds)
        self.assertEqual(cmd[1:2], tl.NOOPT)
        self.assertEqual(len(b''.join(data[:-1])), len(txt + cmd))
        nego.sb_getter = None # break the nego => telnet cycle
        self.tearDown()

    def test_IAC_commands(self):
        # reset our setup
        self.dataq.put([EOF_sigil])
        telnet = telnetlib.Telnet(HOST, self.port)
        self.dataq.join()
        self.tearDown()

        for cmd in self.cmds:
            self._test_command([tl.IAC, cmd, EOF_sigil])
            self._test_command([b'x' * 100, tl.IAC, cmd, b'y'*100, EOF_sigil])
            self._test_command([b'x' * 10, tl.IAC, cmd, b'y'*10, EOF_sigil])
        # all at once
        self._test_command([tl.IAC + cmd for (cmd) in self.cmds] + [EOF_sigil])
        self.assertEqual(b'', telnet.read_sb_data())

    def test_SB_commands(self):
        # RFC 855, subnegotiations portion
        send = [tl.IAC + tl.SB + tl.IAC + tl.SE,
                tl.IAC + tl.SB + tl.IAC + tl.IAC + tl.IAC + tl.SE,
                tl.IAC + tl.SB + tl.IAC + tl.IAC + b'aa' + tl.IAC + tl.SE,
                tl.IAC + tl.SB + b'bb' + tl.IAC + tl.IAC + tl.IAC + tl.SE,
                tl.IAC + tl.SB + b'cc' + tl.IAC + tl.IAC + b'dd' + tl.IAC + tl.SE,
                EOF_sigil,
               ]
        self.dataq.put(send)
        telnet = telnetlib.Telnet(HOST, self.port)
        self.dataq.join()
        nego = nego_collector(telnet.read_sb_data)
        telnet.set_option_negotiation_callback(nego.do_nego)
        txt = telnet.read_all()
        self.assertEqual(txt, b'')
        want_sb_data = tl.IAC + tl.IAC + b'aabb' + tl.IAC + b'cc' + tl.IAC + b'dd'
        self.assertEqual(nego.sb_seen, want_sb_data)
        self.assertEqual(b'', telnet.read_sb_data())
        nego.sb_getter = None # break the nego => telnet cycle

def test_main(verbose=None):
    support.run_unittest(GeneralTests, ReadTests, OptionTests)

if __name__ == '__main__':
    test_main()
