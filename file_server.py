#!/usr/bin/env python

from flask import make_response, request, render_template, send_file, Response
from flask.views import MethodView
from werkzeug.utils import secure_filename
import os
import re
import json
import mimetypes
from uuid import uuid4
import shutil

import prepare_app as prep
import operations
from decorators import path_operation


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


class PathView(MethodView):

    @path_operation()
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
            stat_res = filepath.stat()
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

    @path_operation(authenticate=True, mkdirs=True)
    def put(self, path):
        result_code = 201
        info = {'status': 'success', 'msg': 'File Saved'}

        try:
            filename = secure_filename(path.name)
            storepath = prep.store / str(uuid4())
            with open(storepath, 'wb') as f:
                f.write(request.stream.read())
            (self.dir_path / filename).symlink_to(storepath)
        except Exception as e:
            info['status'] = 'error'
            info['msg'] = str(e)
            result_code = 500

        res = make_response(json.dumps(info), result_code)
        res.headers.add('Content-type', 'application/json')
        return res

    @path_operation(authenticate=True, mkdirs=True, path_is_folder=True)
    def post(self, path):
        result_code = 201
        info = {'status': 'success', 'msg': 'File Saved'}

        files = request.files.getlist('files[]')
        for file in files:
            try:
                filename = secure_filename(file.filename)
                storepath = prep.store / str(uuid4())
                file.save(str(storepath))
                (path / filename).symlink_to(storepath)
            except Exception as e:
                info['status'] = 'error'
                info['msg'] = str(e)
                result_code = 500

        res = make_response(json.dumps(info), result_code)
        res.headers.add('Content-type', 'application/json')
        return res

    @path_operation(authenticate=True, check_dir=True)
    def delete(self, path):
        result_code = 204
        info = {'status': 'success', 'msg': 'File Deleted'}

        try:
            filename = secure_filename(path.name)
            filepath = self.dir_path / filename
            if filepath.is_dir():
                shutil.rmtree(filepath)
            elif filepath.is_file():
                filepath.unlink()
            else:
                result_code = 404
                info = {'status': 'failure', 'msg': 'Not Found'}
        except Exception as e:
            info['status'] = 'error'
            info['msg'] = str(e)
            result_code = 500

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
