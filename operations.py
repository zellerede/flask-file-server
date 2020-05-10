"""
    file operation API endpoints
    current version assumes that all the content in given folders
    are symbolic links to a filestore folder
"""

from flask import Blueprint, make_response, request
import shutil
import requests
from glob import glob
import re

import prepare_app as prep

api = Blueprint('api', __name__, url_prefix='/api/v1')


def copy_links(source, target):
    if source.is_dir():
        shutil.copytree(source, target, symlinks=True)
    elif source.is_file():
        shutil.copy(source, target, follow_symlinks=False)
    else:
        raise Exception(f"404 Unknown source {source}")


@api.route('/copy/<path:source>/', methods=['POST'])
def copy(source):
    return copy_or_move(source, copy_links)


@api.route('/move/<path:source>/', methods=['POST'])
def move(source):
    return copy_or_move(source, prep.Path.rename)


def copy_or_move(source, oper):
    target = request.args.get('to').strip('/')
    result_code = 200
    info = ''
    if target:
        print(f"COPYING/MOVING, {source} -> {target}")
        source_path = (prep.root / source).absolute()
        target_path = (prep.root / target).absolute()
        target_path.mkdir(parents=True, exist_ok=True)
        print(f"{source_path} ==> {target_path}")
        try:
            oper(source_path, target_path)
        except Exception as e:
            print(f"[ERROR] {e}")
            info = str(e)  # TODO: maybe json
            maybe_result_code = info[:3]
            result_code = int(maybe_result_code) if maybe_result_code.isdigit() else 500

    return make_response(info, result_code)


@api.route('/send/', methods=['POST'])
def send():
    data = request.get_json()
    globs = data.get("files")
    assert isinstance(globs, list), "Argument 'files' must be a list"
    target = data.get("target")
    assert isinstance(target, str), "Argument 'target' is obligatory"
    pathmaps = data.get("pathmaps", {})
    assert isinstance(pathmaps, dict), "Argument 'pathmaps' must be a map (str->str)"

    globsets = (set(glob(f"{prep.root}/{g}", recursive=True)) for g in globs)
    filepaths = set.union(*globsets)

    # TODO: launch sending in background, and send back 202
    for path in filepaths:
        relative = prep.relative(path)
        for src, dst in pathmaps.items():
            relative = re.sub(src, dst, relative)
        _send_a_file(path, f"{target}/{relative}")

    return "SUCCESS"  # maybe json


def _send_a_file(source, target):
    if prep.Path(source).is_file():
        print(f"Sending to {target}")
        with open(source, 'rb') as f:
            requests.put(target, data=f)


#!/bin/bash
# data='{"files": ["*"], "target": "http://localhost:8001", "pathmaps": {"t(.*).txt":"utu\\1.txt"}}'
# data='{"files": ["a1/b1/**", "taa/other.txt"], "target": "http://localhost:8001/custom/root"}'
# curl -i -H "Content-type:application/json" localhost:8000/api/v1/send/ -d "$data"