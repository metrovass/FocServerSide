from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from config import Config



db = SQLAlchemy()
socketio = SocketIO( message_queue="redis://localhost:6379")