from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure MySQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:123456@localhost/login'  # Replace with your actual MySQL credentials
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

# Function to automatically hash existing plain text passwords in the database
def hash_existing_passwords():
    users = User.query.all()
    for user in users:
        if len(user.password) < 20:  # Assuming hashed passwords are longer than 20 characters
            print(f"Hashing password for user: {user.username}")
            user.password = generate_password_hash(user.password)
            db.session.add(user)
    try:
        db.session.commit()
        print("All plain text passwords have been hashed.")
    except Exception as e:
        db.session.rollback()
        print(f"Error while hashing passwords: {str(e)}")

# Login route to authenticate users
@app.route('/login', methods=['POST'])
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

# Registration route to save a new user to the database
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')  # Use JSON for simplicity
    password = request.json.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Check if the username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)

    try:
        db.session.commit()  # Commit the transaction
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to register user: " + str(e)}), 500

# Main entry point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
        hash_existing_passwords()  # Optionally hash existing passwords
    app.run(debug=True)
