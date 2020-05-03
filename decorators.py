from functools import wraps
from flask import make_response, request
import json
import prepare_app as prep


def authenticated(func):

    @wraps(func)
    def authenticated_func(*args, **kwargs):
        print(request.cookies.get('auth_cookie'), prep.key)
        if request.cookies.get('auth_cookie') == prep.key:
            res = func(*args, **kwargs)
        else:
            info = {}
            info['status'] = 'error'
            info['msg'] = 'Authentication failed'
            res = make_response(json.dumps(info), 401)
            res.headers.add('Content-type', 'application/json')
        return res

    return authenticated_func


class path_operation:
    """ parametrized decorator """

    def __init__(self, authenticate=False, mkdirs=False):
        self.authenticate = authenticate
        self.mkdirs = mkdirs

    def __call__(self, func):

        @wraps(func)
        def wrapped(self, p=''):
            self.orig_path = p
            path = prep.root / p
            return func(self, path)

        if self.authenticate:
            wrapped = authenticated(wrapped)
        return wrapped
