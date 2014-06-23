import unittest
try:
    from unittest import mock
except ImportError: # PY2
    import mock

from forest import connectors
from .test_core import sample_one, sample_many


class TastyPieConnectorTests(unittest.TestCase):
    def test_get_docs(self):
        conn = connectors.TastyPieConnector('http://api.foo.com/api/v1/')
        self.assertEquals(conn.__get_docs__(sample_many), sample_many['objects'])

    def test_resumption_resource_path(self):
        conn = connectors.TastyPieConnector('http://api.foo.com/api/v1/')
        path, params = conn.__resumption_resource_path__(sample_many)

        self.assertEquals(path, 'journals')
        self.assertEquals(params, {'limit': ['1'], 'collection': ['saude-publica'], 'offset': ['1']})

