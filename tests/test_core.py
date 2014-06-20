import unittest
try:
    from unittest import mock
except ImportError: # PY2
    import mock

from forest import core
from . import doubles


# ------------------------
# Fixtures
# ------------------------
sample_many = {
 u'meta': {u'limit': 1,
           u'next': u'/api/v1/journals/?limit=1&collection=saude-publica&offset=1',
           u'offset': 0,
           u'previous': None,
           u'total_count': 15},
 u'objects': [{u'abstract_keyword_languages': None,
               u'acronym': u'aiss',
               u'issues': [u'/api/v1/issues/1420/',
                           u'/api/v1/issues/3415/'],
               u'print_issn': u'0021-2571',
               u'pub_level': u'CT',
               u'pub_status': u'current',
               u'pub_status_history': [{u'date': u'2010-04-01T00:00:00',
                                        u'status': u'current'}],
               u'publication_city': u'Roma',
               u'publisher_country': u'IT',
               u'publisher_name': u'Istituto Superiore di Sanit\xe0',
               u'publisher_state': u'Rome',
               u'resource_uri': u'/api/v1/journals/25/',
               u'sections': [u'/api/v1/sections/1129/',
                             u'/api/v1/sections/1619/'],
               u'study_areas': [u'Health Sciences'],
               u'title': u"Annali dell'Istituto Superiore di Sanit\xe0",
               u'use_license': {u'disclaimer': u'<p> </p>',
                                u'resource_uri': u'/api/v1/uselicenses/1044/'}}]}

sample_one = sample_many['objects'][0]


# ------------------------
# Unit tests
# ------------------------
class ConnectorTests(unittest.TestCase):

    def test_basic_init_state(self):
        conn = core.Connector('http://api.foo.com/api/v1/')
        self.assertEqual(conn.api_uri, 'http://api.foo.com/api/v1/')
        self.assertEqual(conn.auth, None)
        self.assertEqual(conn.items_per_request, 50)
        self.assertEqual(conn.check_ca, False)

    def test_fetch_data(self):
        mock_get = mock.MagicMock()
        mock_get.return_value = sample_one

        fake_httpbroker = doubles.make_fake_httpbroker()
        fake_httpbroker.get = mock_get

        with mock.patch.dict('forest.core.__dict__', httpbroker=fake_httpbroker):
            conn = core.Connector('http://api.foo.com/api/v1/')

            self.assertEquals(sample_one, conn.fetch_data('/journals/2/'))
            self.assertEquals(fake_httpbroker.get.call_args,
                              mock.call('http://api.foo.com/api/v1/journals/2/',
                                        params=None,
                                        auth=None))

