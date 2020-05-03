"""
    file operation API endpoints
"""

from flask import Blueprint, make_response, request
import prepare_app as prep

api = Blueprint('api', __name__, url_prefix='/api/v1')


def symlink(source, target):
    target.symlink_to(source)


@api.route('/copy/<path:source>/', methods=['POST'])
def copy(source=''):
    return copy_or_move(source, symlink)


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
            result_code = 500

    return make_response(info, result_code)
