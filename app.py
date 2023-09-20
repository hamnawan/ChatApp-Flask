# app.py
from flask import Flask
from .config import Config
from models import db
from routes import api_bp
from socketio import socketio

app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(api_bp, url_prefix='/api')
socketio.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    socketio.run(app, debug=True)

