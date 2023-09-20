# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()


# Create a User model


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    chatroom = db.relationship('ChatRoom', secondary='user_chatroom', back_populates='users')
    messages = db.relationship('Message', back_populates='user')


# Create a ChatRoom Model


class ChatRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    users = db.relationship('User', secondary='user_chatroom', back_populates='chatroom')
    messages = db.relationship('Message', backref='chatroom', lazy=True)


# Create an association table for the many-to-many relationship between User and ChatRoom


user_chatroom = db.Table('user_chatroom',
                         db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                         db.Column('chatroom_id', db.Integer, db.ForeignKey('chat_room.id'), primary_key=True)
                         )


# Create a Message Model


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chatroom_id = db.Column(db.Integer, db.ForeignKey('chat_room.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', back_populates='messages')
