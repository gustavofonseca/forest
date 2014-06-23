import urllib
try:
    from urllib import parse
except ImportError:  # PY2
    import urlparse as parse

from .core import Connector


class TastyPieConnector(Connector):
    def __get_docs__(self, data):
        """Documents are grouped under `objects`.
        """
        return data['objects']

    def __resumption_resource_path__(self, data):
        """Tastypie's URIs are things like:
        u'/api/v1/journals/?limit=1&collection=saude-publica&offset=1'

        And we must return:
        ('journals', {u'limit': [u'1'], u'collection': [u'saude-publica'], u'offset': [u'1']})
        """
        uri_next = data['meta']['next']
        if uri_next is None:
            raise ValueError('Missing resumption resource path')

        parsed = parse.urlparse(uri_next)

        path = parsed.path.rsplit('/', 2)[1]
        querystr = parse.parse_qs(parsed.query)

        return path, querystr

