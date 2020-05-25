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

    def __init__(self, authenticate=False, mkdirs=False, path_is_folder=False,
                 check_dir=False):
        self.authenticate = authenticate
        self.mkdirs = mkdirs
        self.path_is_folder = path_is_folder
        self.chkdir = check_dir

    def __call__(self, func):

        @wraps(func)
        def wrapped(_self, p=''):
            if p.startswith('api/'):
                return self.json404()

            _self.paths = prep.Path(p).parts
            path = prep.root / p
            _self.dir_path = path if self.path_is_folder else path.parent
            if self.mkdirs:
                _self.dir_path.mkdir(parents=True, exist_ok=True)
            res = (self.chkdir or self.mkdirs) and self.check_dir(_self.dir_path)
            return res or func(_self, path)

        if self.authenticate and prep.key:
            wrapped = authenticated(wrapped)
        return wrapped

    def check_dir(self, dir_path):
        if not dir_path.is_dir():
            print(f"Wrong folder: {dir_path}")  ###
            return self.json404()

    def json404(self):
        info = {'status': 'error', 'msg': 'Invalid Operation'}
        res = make_response(json.dumps(info), 404)
        res.headers.add('Content-type', 'application/json')
        return res
