# coding: utf-8
from __future__ import unicode_literals
import logging


logger = logging.getLogger(__name__)


class Connector(object):
    """
    Encapsulates the HTTP requests layer.

    :param api_uri: Full path to the API. e.g.: `http://manager.scielo.org/api/v1/`.
    :param auth: (optional) `requests.auth.AuthBase` subclass.
    :param items_per_request: (optional) how many items are retrieved per request.
    Defaults to `50`.
    :param check_ca: (optional) if certification authority should be checked during
    ssl sessions. Defaults to `False`.
    """

    def __init__(self, api_uri, auth=None, items_per_request=50, check_ca=False):
        self.api_uri = api_uri
        self.auth = auth
        self.items_per_request = items_per_request
        self.check_ca = check_ca

