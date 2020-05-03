#!/usr/bin/env python

from flask import make_response, request, render_template, send_file, Response
from flask.views import MethodView
from werkzeug import secure_filename
import os
import re
import json
import mimetypes
from functools import wraps

import prepare_app as prep
import operations


def partial_response(path, start, end=None):
    file_size = os.path.getsize(path)

    if end is None:
        end = file_size - start - 1
    end = min(end, file_size - 1)
    length = end - start + 1

    with open(path, 'rb') as fd:
        fd.seek(start)
        _bytes = fd.read(length)
    assert len(_bytes) == length

    response = Response(
        _bytes,
        206,
        mimetype=mimetypes.guess_type(path)[0],
        direct_passthrough=True,
    )
    response.headers.add(
        'Content-Range', f'bytes {start}-{end}/{file_size}'
    )
    response.headers.add(
        'Accept-Ranges', 'bytes'
    )
    return response


def get_range(request):
    range = request.headers.get('Range')
    m = re.match(r'bytes=(?P<start>\d+)-(?P<end>\d+)?', range)
    if m:
        start = m.group('start')
        end = m.group('end')
        start = int(start)
        if end is not None:
            end = int(end)
        return start, end
    else:
        return 0, None


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


def path_operation(func):
    @wraps(func)
    def wrapped(self, p=''):
        self.orig_path = p
        path = prep.root / p
        return func(self, path)
    return wrapped


class PathView(MethodView):

    @path_operation
    def get(self, path):
        if path.is_dir():
            res = self._get_dir(path)
        elif path.is_file():
            if 'Range' in request.headers:
                start, end = get_range(request)
                res = partial_response(path, start, end)
            else:
                res = send_file(path)
                res.headers.add('Content-Disposition', 'attachment')
        else:
            res = make_response('Not found', 404)
        return res

    def _get_dir(self, path):
        hide_dotfile = request.args.get('hide-dotfile', request.cookies.get('hide-dotfile', 'no'))
        contents = []
        total = {'size': 0, 'dir': 0, 'file': 0}
        for filename in os.listdir(path):
            if filename in prep.ignored:
                continue
            if hide_dotfile == 'yes' and filename.startswith('.'):
                continue
            filepath = path / filename
            stat_res = filepath.lstat()
            info = {}
            info['name'] = filename
            info['mtime'] = stat_res.st_mtime
            ft = 'dir' if filepath.is_dir() else 'file'
            info['type'] = ft
            total[ft] += 1
            sz = stat_res.st_size
            info['size'] = sz
            total['size'] += sz
            contents.append(info)
        page = render_template('index.html', path=self.orig_path, contents=contents, total=total, hide_dotfile=hide_dotfile)
        res = make_response(page, 200)
        res.set_cookie('hide-dotfile', hide_dotfile, max_age=16070400)
        # TODO: answer json if json was requested
        return res

    @path_operation
    @authenticated
    def put(self, path):
        dir_path = path.parent
        dir_path.mkdir(parents=True, exist_ok=True)

        result_code = 201
        info = {}
        if dir_path.is_dir():
            try:
                filename = secure_filename(path.name)
                with open(dir_path / filename, 'wb') as f:
                    f.write(request.stream.read())
            except Exception as e:
                info['status'] = 'error'
                info['msg'] = str(e)
                result_code = 500
            else:
                info['status'] = 'success'
                info['msg'] = 'File Saved'
        else:
            info['status'] = 'error'
            info['msg'] = 'Invalid Operation'
            result_code = 404
        res = make_response(json.dumps(info), result_code)
        res.headers.add('Content-type', 'application/json')
        return res

    @path_operation
    @authenticated
    def post(self, path):
        path.mkdir(parents=True, exist_ok=True)

        result_code = 201
        info = {}
        if path.is_dir():
            files = request.files.getlist('files[]')
            for file in files:
                try:
                    filename = secure_filename(file.filename)
                    file.save(str(path / filename))
                except Exception as e:
                    info['status'] = 'error'
                    info['msg'] = str(e)
                    result_code = 500
                else:
                    info['status'] = 'success'
                    info['msg'] = 'File Saved'
        else:
            info['status'] = 'error'
            info['msg'] = 'Invalid Operation'
            result_code = 404
        res = make_response(json.dumps(info), result_code)
        res.headers.add('Content-type', 'application/json')
        return res

    @path_operation
    @authenticated
    def delete(self, path):
        dir_path = path.parent

        result_code = 204
        info = {}
        if dir_path.is_dir():
            try:
                filename = secure_filename(path.name)
                (dir_path / filename).unlink()
                # os.rmdir(dir_path) # shutils.rmtree
            except Exception as e:
                info['status'] = 'error'
                info['msg'] = str(e)
                result_code = 500
            else:
                info['status'] = 'success'
                info['msg'] = 'File Deleted'
        else:
            info['status'] = 'error'
            info['msg'] = 'Invalid Operation'
            result_code = 404
        res = make_response(json.dumps(info), result_code)
        res.headers.add('Content-type', 'application/json')
        return res


app = prep.app
path_view = PathView.as_view('path_view')
app.register_blueprint(operations.api)
app.add_url_rule('/', view_func=path_view)
app.add_url_rule('/<path:p>', view_func=path_view)

if __name__ == '__main__':
    bind = os.getenv('FS_BIND', '0.0.0.0')
    port = os.getenv('FS_PORT', '8000')
    app.run(bind, port, threaded=True, debug=False)
