import unittest
import sqroot

class MockSocket:
    def __init__(self):
        self._buffer = b""

    def sendall(self, data: bytes):
        coeffs = data.decode().strip()
        try:
            result = sqroot.sqroots(coeffs)
        except:
            result = ""
        self._buffer = (result + "\n").encode()

    def recv(self, _):
        return self._buffer

class TestSqrootnetMock(unittest.TestCase):
    def setUp(self):
        self.s = MockSocket()

    def test_two_roots(self):
        self.assertEqual(sqroot.sqrootnet("1 -3 2", self.s), "1.0 2.0")

    def test_one_root(self):
        self.assertEqual(sqroot.sqrootnet("1 2 1", self.s), "-1.0")

    def test_no_roots(self):
        self.assertEqual(sqroot.sqrootnet("1 0 1", self.s), "")

    def test_invalid(self):
        self.assertEqual(sqroot.sqrootnet("abc def", self.s), "")

