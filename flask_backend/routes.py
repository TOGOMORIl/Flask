from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_backend.model import User, db
from flask_backend.register import Register


# Define a Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if user is None or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({"message": "Login successful!", "username": username}), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    username = data.get('username')
    password = data.get('password')

    # Create a Register object
    registration = Register(username, password)

    # Call the register_user method
    response, status_code = registration.register_user()
    return jsonify(response), status_code



