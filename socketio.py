# socketio.py
from flask_socketio import SocketIO, emit
from flask import request, jsonify
import jwt
from models import db, User, ChatRoom, Message

socketio = SocketIO()


# WebSocket route for real-time chat
@socketio.on('message')
def join_chat_room(room_id):
    data = request.get_json()
    token = data.get('token')

    try:
        decoded_token = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

    user_id = decoded_token['user_id']
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    chat_room = ChatRoom.query.get(room_id)

    if not chat_room:
        return jsonify({'message': 'Chat room not found'}), 404

    join_room(str(room_id))
    return jsonify({'message': 'Joined chat room'}), 200
