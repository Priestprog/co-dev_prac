import unittest
import socket
import time
import multiprocessing
import sqroot


class TestServerNet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proc = multiprocessing.Process(target=sqroot.sqrootnet)
        cls.proc.start()
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.join()

    def setUp(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(("127.0.0.1", 1337))

    def tearDown(self):
        self.s.close()

    def test_two_roots(self):
        self.assertEqual(sqroot.sqrootnet("1 -3 2", self.s), "1.0 2.0")

    def test_one_root(self):
        self.assertEqual(sqroot.sqrootnet("1 2 1", self.s), "-1.0")

    def test_no_roots(self):
        self.assertEqual(sqroot.sqrootnet("1 0 1", self.s), "")

    def test_invalid(self):
        self.assertEqual(sqroot.sqrootnet("0 2 1", self.s), "")

