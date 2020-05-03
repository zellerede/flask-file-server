"""
    file operation API endpoints
    current version assumes that all the content in given folders
    are symbolic links to a filestore folder
"""

from flask import Blueprint, make_response, request
import shutil
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
def copy(source=''):
    return copy_or_move(source, copy_links)


@api.route('/move/<path:source>/', methods=['POST'])
def move(source=''):
    return copy_or_move(source, prep.Path.rename)


def copy_or_move(source, oper):
    target = request.args.get('to').strip('/')
    result_code = 200
    info = ''
    if target:
        print(f"COPYING/MOVING, {source} -> {target}")
        source_path = (prep.root / source).absolute()
        target_path = (prep.root / target).absolute()
        print(f"{source_path} ==> {target_path}")
        try:
            oper(source_path, target_path)
        except Exception as e:
            print(f"[ERROR] {e}")
            info = str(e)  # TODO: maybe json
            maybe_result_code = info[:3]
            result_code = int(maybe_result_code) if maybe_result_code.isdigit() else 500

    return make_response(info, result_code)
