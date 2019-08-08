from flask import Flask

from extensions import socketio, bootstrap, db

from edge import edge_bp
from cloud import cloud_bp


def create_app():

    app = Flask(__name__)

    app.config['SECRET'] = 'my secret key'
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@127.0.0.1:3306/cloud_db'  # noqa
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False

    socketio.init_app(app, async_mode=None)
    bootstrap.init_app(app)
    db.init_app(app)

    app.register_blueprint(edge_bp)
    app.register_blueprint(cloud_bp)
    return app


if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=True, debug=True)
