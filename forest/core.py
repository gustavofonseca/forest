# coding: utf-8
from __future__ import unicode_literals
import logging
import time

from . import httpbroker
from . import exceptions


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
    :param max_retries: (optional) max retries before aborting on
    connection failures.
    :param retry_timeout_factor: (optional) waits
    `retry_timeout_factor` * `retry_count` before firing a new request.
    """

    def __init__(self, api_uri, auth=None, items_per_request=50,
                 check_ca=False, max_retries=5, retry_timeout_factor=0):
        self.api_uri = api_uri
        self.auth = auth
        self.items_per_request = items_per_request
        self.check_ca = check_ca

        self.max_retries = max_retries
        self.retry_timeout_factor = retry_timeout_factor

    def fetch_data(self, resource_path=None, params=None):
        """
        Fetches the specified resource.

        :param resource_path: (optional) the endpoint and resource id.
        :param params: (optional) params to be passed as query string.
        """
        err_count = 0
        resource_url = httpbroker._make_full_url(self.api_uri, resource_path)

        while True:
            try:
                response = httpbroker.get(resource_url,
                                          auth=self.auth,
                                          params=params)

            except (exceptions.ConnectionError, exceptions.ServiceUnavailable) as e:
                if err_count < self.max_retries:
                    wait_secs = err_count * self.retry_timeout_factor
                    logger.info('%s. Waiting %ss to retry.' % (e, wait_secs))
                    time.sleep(wait_secs)
                    err_count += 1
                    continue
                else:
                    logger.error('%s. Unable to connect to resource.' % e)
                    raise
            else:
                return response

    def iter_docs(self, resource_path=None, params=None):
        """
        Iterates over all documents of a given endpoint and collection.

        :param resource_path: (optional) the endpoint and resource id.
        :param params: (optional) params to be passed as query string.
        """
        data = self.fetch_data(resource_path, params)

        while True:
            for obj in self.__get_docs__(data):
                yield obj

            try:
                res_path, res_params = self.__resumption_resource_path__(data)
            except ValueError:
                raise StopIteration()

            data = self.fetch_data(res_path, res_params)

    def __get_docs__(self, data):
        """Returns the iterable that will be consumed by iter_docs.
        """
        #return data['objects']
        raise NotImplementedError()

    def __resumption_resource_path__(self, data):
        """Returns a pair of resource_path and params, just like
        `iter_docs` or `fetch_data` would accept.
        """
        #return data['meta']['next']
        raise NotImplementedError()

