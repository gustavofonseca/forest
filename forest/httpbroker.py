# coding: utf-8
from __future__ import unicode_literals
from functools import wraps
import json
import logging

import requests

from . import exceptions, compat


__all__ = ['get', 'post', '_make_full_url']

DEFAULT_SCHEME = 'http'
DEFAULT_USER_AGENT = 'scielo-client'

logger = logging.getLogger(__name__)


def check_http_status(response):
    """
    Raises one of `scieloapi.exceptions` depending on response status-code.

    :param response: is a requests.Response instance.
    """
    http_status = response.status_code

    logger.debug('Response status code is %s' % http_status)

    if http_status == 400:
        raise exceptions.BadRequest()
    elif http_status == 401:
        raise exceptions.Unauthorized()
    elif http_status == 403:
        raise exceptions.Forbidden()
    elif http_status == 404:
        raise exceptions.NotFound()
    elif http_status == 405:
        raise exceptions.MethodNotAllowed()
    elif http_status == 406:
        raise exceptions.NotAcceptable()
    elif http_status == 500:
        raise exceptions.InternalServerError()
    elif http_status == 502:
        raise exceptions.BadGateway()
    elif http_status == 503:
        raise exceptions.ServiceUnavailable()
    else:
        return None


def translate_exceptions(func):
    """
    Translates all dependencies' exceptions and re-raise them as scieloapi's.

    This function aims to isolate third-party dependencies from the exposed
    API, in a way users should never import `requests` lib to handle exceptions
    or other stuff.
    """
    @wraps(func)
    def f_wrap(*args, **kwargs):
        try:
            resp = func(*args, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise exceptions.ConnectionError(e)
        except requests.exceptions.HTTPError as e:
            raise exceptions.HTTPError(e)
        except requests.exceptions.Timeout as e:
            raise exceptions.Timeout(e)
        except requests.exceptions.TooManyRedirects as e:
            raise exceptions.HTTPError(e)
        except requests.exceptions.RequestException as e:
            raise exceptions.HTTPError(e)
        else:
            return resp

    return f_wrap


def prepare_params(params):
    """
    Prepare params before the http request is dispatched.

    The return value must be a list of doubles (tuples of lenght 2). By now,
    the preparation step basically transforms `params` to the right return type
    sorted by keys.

    In cases where `params` is None, None must be returned.

    :param params: Is key/value pair or `None`.
    """
    if params is None:
        return None

    if hasattr(params, 'items'):
        params = params.items()

    return sorted(params)


def prepare_data(data):
    """
    Prepare data to be dispatched.

    If `data` is a byte string, nothing is done, else `data` is
    encoded as JSON.

    :param data: json serializable data
    """
    prepared = data if isinstance(data, compat.string_types) else json.dumps(data)
    return prepared



def _make_full_url(*uri_segs):
    """
    Joins URI segments to produce an URL.

    URI segments are passed as positional args and placed in order
    to produce a valid URL. Trailing slashes and HTTP scheme are
    added automatically.
    """
    full_uri = '/'.join([str(seg).strip('/') for seg in uri_segs if seg])

    if not full_uri.endswith('/'):
        full_uri += '/'
    if not full_uri.startswith('http'):
        full_uri = DEFAULT_SCHEME + '://' + full_uri

    return full_uri


@translate_exceptions
def get(url, params=None, auth=None, check_ca=False, user_agent=None):
    """
    Dispatches an HTTP GET request to `url`.

    This function is tied to some concepts of Restful interfaces
    like endpoints and resource ids. Any querystring params must
    be passed as dictionaries to `params`.

    :param url: A resource's url.
    :param params: (optional) params to be passed as query string.
    :param auth: (optional) instance of `forest.auth.AuthBase`.
    :param check_ca: (optional) if certification authority should be checked during
    ssl sessions. Defaults to `False`.
    :param user_agent: (optional) string of the user agent.
    """
    # custom headers
    headers = {'User-Agent': user_agent or DEFAULT_USER_AGENT}

    optionals = {}
    if auth:
        optionals['auth'] = auth

    if url.startswith('https'):
        optionals['verify'] = check_ca

    logger.debug('Sending a GET request to %s with headers %s and params %s %s' %
        (url, headers, params, optionals))

    resp = requests.get(url,
                        headers=headers,
                        params=prepare_params(params),
                        **optionals)

    # check if an exception should be raised based on http status code
    check_http_status(resp)

    return resp.json()


def post(url, data, auth=None, check_ca=False, user_agent=None):
    """
    Dispatches an HTTP POST request to `api_uri`, with `data`.

    This function is tied to some concepts of Restful interfaces
    like endpoints. A new resource is created and its URL is
    returned.

    :param url: e.g. http://manager.scielo.org/api/v1/journals/
    :param data: json serializable Python datastructures.
    :param auth: (optional) `forest.auth.AuthBase` instance.
    :param check_ca: (optional) if certification authority should be checked during ssl sessions. Defaults to `False`.
    :param user_agent: (optional) string of the user agent.
    :returns: newly created resource url
    """
    # custom headers
    headers = {'User-Agent': user_agent or DEFAULT_USER_AGENT,
               'Content-Type': 'application/json'}

    optionals = {}
    if auth:
        optionals['auth'] = auth

    if url.startswith('https'):
        optionals['verify'] = check_ca

    prepared_data = prepare_data(data)
    logger.debug('Sending a POST request to %s with headers %s, data %s and params %s' %
        (url, headers, prepared_data, optionals))

    resp = requests.post(url=url,
                         data=prepared_data,
                         headers=headers,
                         **optionals)

    # check if an exception should be raised based on http status code
    check_http_status(resp)

    if resp.status_code != 201:
        raise exceptions.APIError('The server has gone nuts: %s' % resp.status_code)

    logger.info('Newly created resource at %s' % resp.headers['location'])

    return resp.headers['location']

