"""Collection of stubs, mocks, fakes and dummies objects.
"""
# coding: utf-8
import types


class RequestsResponseStub(object):
    """
    Pretend to be a requests.Response object.
    """
    def __init__(self, *args, **kwargs):
        self.status_code = 200

    def json(self):
        return {'foo': 'bar'}


# --------------------------------
# `forest.httpbroker` doubles
# --------------------------------
def make_fake_httpbroker(ignore=None):
    """Produces a clone of `forest.httpbroker` module
    containing only public objects, except the ones
    listed in `ignore`.
    """
    from forest import httpbroker
    ignore = ignore or ['get', 'post']

    # relies on the module having an __all__ variable.
    public_members = httpbroker.__all__

    fake_mod = types.ModuleType('httpbroker')
    for member in public_members:
        if member not in ignore:
            setattr(fake_mod, member, getattr(httpbroker, member))

    return fake_mod

