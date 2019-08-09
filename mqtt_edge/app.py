import os
from flask import Flask, render_template, request
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError

from extensions import socketio, bootstrap, db
from utils.sql_utils import fetchone
from logger import log

from edge import edge_bp
from cloud import cloud_bp


_default_instance_path = '%(instance_path)s/instance' % \
                         {'instance_path': os.path.dirname(
                             os.path.realpath(__file__))}


def create_app():

    app = Flask(__name__, instance_relative_config=True,
                instance_path=_default_instance_path)

    app.config.from_pyfile('config.py')

    socketio.init_app(app, async_mode=None)
    bootstrap.init_app(app)
    db.init_app(app)

    register_blueprint(app)
    return app


def register_blueprint(app):
    app.register_blueprint(edge_bp)
    app.register_blueprint(cloud_bp)


app = create_app()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/config', methods=['POST'])
def set_config():
    host = request.form.get('host', '127.0.0.1')
    port = request.form.get('port', '1883')
    sqlite_path = request.form.get('sqlite', './sqlite.db')
    params = {'host': host, 'port': port, 'path': sqlite_path}
    if fetchone('select broker_host from config'):
        sql = text('''
            update config
            set
                broker_host=:host, broker_port=:port, sqlite_path=:path
            ''')
    else:
        sql = text('insert into config values (:host, :port, :path)')
    try:
        db.session.execute(sql, params)
        db.session.commit()
    except DatabaseError as e:
        log.error(e)
        return 'Error'

    return 'Succeeded'


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=True, debug=True)
