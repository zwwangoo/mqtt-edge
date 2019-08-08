from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO

socketio = SocketIO()
bootstrap = Bootstrap()

db = SQLAlchemy()
