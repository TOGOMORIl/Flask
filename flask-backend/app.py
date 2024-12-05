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
        # Check if the password is already hashed (assuming hashed passwords are longer than 20 characters)
        if len(user.password) < 20:
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

    # Check if the user exists in the database
    user = User.query.filter_by(username=username).first()

    if user is None:
        print("Debug: User not found")  # Debugging statement
        return jsonify({"error": "Invalid username or password"}), 401

    # Check password hash
    password_match = check_password_hash(user.password, password)
    print(f"Debug: Stored hash: {user.password}")  # Debugging statement
    print(f"Debug: Provided password: {password}")  # Debugging statement
    print(f"Debug: Password hash comparison result: {password_match}")  # Debugging statement

    if not password_match:
        print("Debug: Password did not match")  # Debugging statement
        return jsonify({"error": "Invalid username or password"}), 401

    print("Debug: Login successful")  # Debugging statement
    return jsonify({"message": "Login successful!", "username": username}), 200

if __name__ == '__main__':
    with app.app_context():
        hash_existing_passwords()
    app.run(debug=True)
