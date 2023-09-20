# routes.py
from flask import Blueprint, request, jsonify
import jwt
from .models import db, bcrypt, User, ChatRoom, Message
from datetime import datetime, timedelta
from .socketio import socketio  # Import socketio from socketio.py

api_bp = Blueprint('api', __name__)


# API route for user registration
@api_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    # Check if the username already exists in the database
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=username, password=hashed_password)

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


# API route for user login
@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Include the 'user_id' claim in the JWT token
    token_payload = {'user_id': user.id, 'exp': datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA']}

    # Generate a JWT token with the 'user_id' claim
    token = jwt.encode(token_payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')

    return jsonify({'message': 'Login successful', 'token': token})


# API route for user logout


@api_bp.route('/api/logout', methods=['POST'])
def logout():
    # Implement JWT-based logout if needed
    return jsonify({'message': 'Logout successful'}), 200


# API route for getting a list of chat rooms


@api_bp.route('/api/chat/rooms', methods=['GET'])
def get_chat_rooms():
    chat_rooms = ChatRoom.query.all()
    chat_rooms_data = [{'id': room.id, 'name': room.name, 'description': room.description} for room in chat_rooms]
    return jsonify({'chat_rooms': chat_rooms_data}), 200


# API route for creating a new chat room


@api_bp.route('/api/chat/rooms', methods=['POST'])
def create_chat_room():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name:
        return jsonify({'message': 'Chat room name is required'}), 400

    chat_room = ChatRoom(name=name, description=description)
    db.session.add(chat_room)
    db.session.commit()

    return jsonify({'message': 'Chat room created successfully'}), 201


# API route for getting the details of a specific chat room


@api_bp.route('/api/chat/rooms/<int:room_id>', methods=['GET'])
def get_chat_room_details(room_id):
    chat_room = ChatRoom.query.get(room_id)

    if not chat_room:
        return jsonify({'message': 'Chat room not found'}), 404

    chat_room_data = {
        'id': chat_room.id,
        'name': chat_room.name,
        'description': chat_room.description,
        'users': [{'id': user.id, 'username': user.username} for user in chat_room.users],
        'messages': [{'id': message.id, 'content': message.content, 'user_id': message.user_id} for message in
                     chat_room.messages]
    }

    return jsonify({'chat_room': chat_room_data}), 200


# API route for allowing a user to send a message to a specific chat room
@api_bp.route('/api/chat/rooms/<int:room_id>/messages', methods=['POST'])
def send_message_to_chat_room(room_id):
    data = request.get_json()
    token = data.get('token')
    message_content = data.get('message')

    if not message_content:
        return jsonify({'message': 'Message content is required'}), 400

    # Ensure user is authenticated using JWT
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

    # Check if the user is not already a member of the chat room, and if not, add them.
    if user not in chat_room.users:
        chat_room.users.append(user)
        db.session.commit()

    # Now that the user is a member (if they weren't already), proceed to send the message.
    message = Message(content=message_content, user_id=user_id, chatroom_id=room_id)
    db.session.add(message)
    db.session.commit()

    # Broadcast the message to all users in the chat room
    socketio.emit('message', {'sender_id': user_id, 'text': message_content, 'created_at': message.timestamp},
                  room=str(room_id))

    return jsonify({'message': 'Message sent successfully'}), 201


#  API route for getting a list of messages for a specific chat room.


@api_bp.route('/api/chat/rooms/<int:room_id>/messages', methods=['GET'])
def get_chat_room_messages(room_id):
    chat_room = ChatRoom.query.get(room_id)

    if not chat_room:
        return jsonify({'message': 'Chat room not found'}), 404

    messages = Message.query.filter_by(chatroom_id=room_id).all()

    messages_data = [{'id': message.id, 'content': message.content, 'sender_id': message.user_id,
                      'created_at': message.timestamp} for message in messages]

    # Include the chat room ID in the response
    response_data = {'chat_room_id': chat_room.id, 'messages': messages_data}

    return jsonify(response_data), 200

