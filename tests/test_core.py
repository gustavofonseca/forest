import unittest

from forest import core


class ConnectorTests(unittest.TestCase):

    def test_basic_init_state(self):
        conn = core.Connector('http://api.foo.com/api/v1/')
        self.assertEqual(conn.api_uri, 'http://api.foo.com/api/v1/')
        self.assertEqual(conn.auth, None)
        self.assertEqual(conn.items_per_request, 50)
        self.assertEqual(conn.check_ca, False)

