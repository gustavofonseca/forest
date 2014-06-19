# coding: utf-8
from __future__ import unicode_literals


class AuthBase(object):
    """Base class that all auth implementations derive from.

    This class is heavily based on requests' `auth.AuthBase`.
    """

    def __call__(self, r):
        raise NotImplementedError('Auth hooks must be callable.')


class ApiKeyAuth(AuthBase):
    """Tastypie's ApiKey based authentication.
    """
    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key

    def __call__(self, r):
        """
        Adds the Authorization header as listed in
        http://ref.scielo.org/ddkpmx
        """
        auth_string = ' ApiKey %s:%s' % (self.username, self.api_key)
        r.headers['Authorization'] = auth_string
        return r

