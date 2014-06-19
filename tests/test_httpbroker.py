import unittest
try:
    from unittest import mock
except ImportError: # PY2
    import mock

import requests

from forest import httpbroker, exceptions
from . import doubles


class CheckHttpStatusTests(unittest.TestCase):

    def test_400_raises_BadRequest(self):
        response = doubles.RequestsResponseStub()
        response.status_code = 400

        self.assertRaises(exceptions.BadRequest,
            lambda: httpbroker.check_http_status(response))

    def test_401_raises_Unauthorized(self):
        response = doubles.RequestsResponseStub()
        response.status_code = 401

        self.assertRaises(exceptions.Unauthorized,
            lambda: httpbroker.check_http_status(response))

    def test_403_raises_Forbidden(self):
        response = doubles.RequestsResponseStub()
        response.status_code = 403

        self.assertRaises(exceptions.Forbidden,
            lambda: httpbroker.check_http_status(response))

    def test_404_raises_NotFound(self):
        response = doubles.RequestsResponseStub()
        response.status_code = 404

        self.assertRaises(exceptions.NotFound,
            lambda: httpbroker.check_http_status(response))

    def test_405_raises_NotFound(self):
        response = doubles.RequestsResponseStub()
        response.status_code = 405

        self.assertRaises(exceptions.MethodNotAllowed,
            lambda: httpbroker.check_http_status(response))

    def test_406_raises_NotAcceptable(self):
        response = doubles.RequestsResponseStub()
        response.status_code = 406

        self.assertRaises(exceptions.NotAcceptable,
            lambda: httpbroker.check_http_status(response))

    def test_500_raises_InternalServerError(self):
        response = doubles.RequestsResponseStub()
        response.status_code = 500

        self.assertRaises(exceptions.InternalServerError,
            lambda: httpbroker.check_http_status(response))

    def test_502_raises_BadGateway(self):
        response = doubles.RequestsResponseStub()
        response.status_code = 502

        self.assertRaises(exceptions.BadGateway,
            lambda: httpbroker.check_http_status(response))

    def test_503_raises_ServiceUnavailable(self):
        response = doubles.RequestsResponseStub()
        response.status_code = 503

        self.assertRaises(exceptions.ServiceUnavailable,
            lambda: httpbroker.check_http_status(response))

    def test_200_returns_None(self):
        response = doubles.RequestsResponseStub()
        response.status_code = 200

        self.assertIsNone(httpbroker.check_http_status(response))


class TranslateExceptionsTests(unittest.TestCase):

    def test_from_ConnectionError_to_ConnectionError(self):
        """
        from requests.exceptions.ConnectionError
        to scieloapi.exceptions.ConnectionError
        """
        @httpbroker.translate_exceptions
        def foo():
            raise requests.exceptions.ConnectionError()

        self.assertRaises(exceptions.ConnectionError,
            lambda: foo())

    def test_from_HTTPError_to_HTTPError(self):
        """
        from requests.exceptions.HTTPError
        to scieloapi.exceptions.HTTPError
        """
        @httpbroker.translate_exceptions
        def foo():
            raise requests.exceptions.HTTPError()

        self.assertRaises(exceptions.HTTPError,
            lambda: foo())

    def test_from_Timeout_to_Timeout(self):
        """
        from requests.exceptions.Timeout
        to scieloapi.exceptions.Timeout
        """
        @httpbroker.translate_exceptions
        def foo():
            raise requests.exceptions.Timeout()

        self.assertRaises(exceptions.Timeout,
            lambda: foo())

    def test_from_TooManyRedirects_to_HTTPError(self):
        """
        from requests.exceptions.TooManyRedirects
        to scieloapi.exceptions.HTTPError
        """
        @httpbroker.translate_exceptions
        def foo():
            raise requests.exceptions.TooManyRedirects()

        self.assertRaises(exceptions.HTTPError,
            lambda: foo())

    def test_from_RequestException_to_HTTPError(self):
        """
        from requests.exceptions.RequestException
        to scieloapi.exceptions.HTTPError
        """
        @httpbroker.translate_exceptions
        def foo():
            raise requests.exceptions.RequestException()

        self.assertRaises(exceptions.HTTPError,
            lambda: foo())


class PrepareParamsFunctionTests(unittest.TestCase):

    def test_sort_dict_by_key(self):
        params = {'username': 1, 'api_key': 2, 'c': 3}

        self.assertEqual(httpbroker.prepare_params(params),
            [('api_key', 2), ('c', 3), ('username', 1)])

    def test_sort_list_of_tuples(self):
        params = [('username', 1), ('api_key', 2), ('c', 3)]

        self.assertEqual(httpbroker.prepare_params(params),
            [('api_key', 2), ('c', 3), ('username', 1)])

    def test_None_returns_None(self):
        params = None

        self.assertIsNone(httpbroker.prepare_params(params))


class GetFunctionTests(unittest.TestCase):

    def test_user_agent_is_properly_set(self):
        """
        By properly I mean: scieloapi/:version, e.g.
        scieloapi/0.4
        """
        mock_requests = mock.MagicMock()
        mock_requests.get.return_value = doubles.RequestsResponseStub()

        with mock.patch.dict('forest.httpbroker.__dict__', requests=mock_requests):
            httpbroker.get('http://manager.scielo.org/api/v1/journals/70/',
                           user_agent='scielo.forest')

            self.assertTrue(httpbroker.requests.get.called)
            self.assertEqual(httpbroker.requests.get.call_args,
                             mock.call('http://manager.scielo.org/api/v1/journals/70/',
                                       headers={'User-Agent': 'scielo.forest'},
                                       params=None))

    def test_https_turns_off_ca_cert_verification_by_default(self):
        mock_requests = mock.MagicMock()
        mock_requests.get.return_value = doubles.RequestsResponseStub()

        with mock.patch.dict('forest.httpbroker.__dict__', requests=mock_requests):
            httpbroker.get('https://manager.scielo.org/api/v1/journals/70/',
                           user_agent='scielo.forest')

            self.assertTrue(httpbroker.requests.get.called)
            self.assertEqual(httpbroker.requests.get.call_args,
                             mock.call('https://manager.scielo.org/api/v1/journals/70/',
                                       headers={'User-Agent': 'scielo.forest'},
                                       params=None,
                                       verify=False))

class PostFunctionTests(unittest.TestCase):

    def test_user_agent_and_content_type_are_properly_set(self):
        """
        By properly I mean: scieloapi/:version, e.g.
        scieloapi/0.4
        """
        mock_requests = mock.MagicMock()
        mock_response = doubles.RequestsResponseStub()
        mock_response.status_code = 201
        mock_response.headers = {'location': 'http://manager.scielo.org/api/v1/journals/4/'}
        mock_requests.post.return_value = mock_response

        with mock.patch.dict('forest.httpbroker.__dict__', requests=mock_requests):
            httpbroker.post('http://manager.scielo.org/api/v1/journals/',
                            data='{"title": "foo"}',
                            user_agent='scielo.forest')

            self.assertTrue(httpbroker.requests.post.called)
            self.assertEqual(httpbroker.requests.post.call_args,
                             mock.call(url='http://manager.scielo.org/api/v1/journals/',
                                       headers={'Content-Type': 'application/json',
                                                'User-Agent': 'scielo.forest'},
                                       data='{"title": "foo"}'))

    def test_unexpected_status_code_raises_APIError(self):
        mock_requests = mock.MagicMock()
        mock_response = doubles.RequestsResponseStub()
        mock_response.status_code = 410
        mock_requests.post.return_value = mock_response

        with mock.patch.dict('forest.httpbroker.__dict__', requests=mock_requests):
            self.assertRaises(
                exceptions.APIError,
                lambda: httpbroker.post('http://manager.scielo.org/api/v1/journals/',
                                        data='{"title": "foo"}',
                                        user_agent='scielo.forest'))

    def test_location_header_is_returned(self):
        mock_requests = mock.MagicMock()
        mock_response = doubles.RequestsResponseStub()
        mock_response.status_code = 201
        mock_response.headers = {'location': 'http://manager.scielo.org/api/v1/journals/4/'}
        mock_requests.post.return_value = mock_response

        with mock.patch.dict('forest.httpbroker.__dict__', requests=mock_requests):
            self.assertEquals(
                'http://manager.scielo.org/api/v1/journals/4/',
                httpbroker.post('http://manager.scielo.org/api/v1/journals/',
                                data='{"title": "foo"}',
                                user_agent='scielo.forest'))


class MakeFullUrlFunctionTests(unittest.TestCase):

    def test_missing_trailing_slash(self):
        path_segments = ['http://manager.scielo.org', 'api', 'v1', 'journals']
        self.assertEqual(httpbroker._make_full_url(*path_segments),
            'http://manager.scielo.org/api/v1/journals/')

    def test_missing_scheme(self):
        path_segments = ['manager.scielo.org', 'api', 'v1', 'journals']
        self.assertEqual(httpbroker._make_full_url(*path_segments),
            'http://manager.scielo.org/api/v1/journals/')

    def test_https(self):
        path_segments = ['https://manager.scielo.org', 'api', 'v1', 'journals']
        self.assertEqual(httpbroker._make_full_url(*path_segments),
            'https://manager.scielo.org/api/v1/journals/')

