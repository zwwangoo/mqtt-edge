from flask import Blueprint, render_template
from extensions import socketio

bp = Blueprint('edge', __name__, url_prefix='/edge')


@bp.route('/')
def index():
    return render_template('edge.html')


@bp.route('/on_message')
def message():
    socketio.emit('cloud_log', {'data': 'xxxxxx'}, namespace='/edge')
    return 'ok'
