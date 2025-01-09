from werkzeug.security import generate_password_hash
from flask_backend.model import User, db

class Register:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def validate_input(self):
        # Validate username and password
        if not self.username or not self.password:
            return {"error": "Username and password are required"}, 400
        return None

    def check_existing_user(self):
        # Check if the username already exists
        existing_user = User.query.filter_by(username=self.username).first()
        if existing_user:
            return {"error": "Username already exists"}, 400
        return None

    def register_user(self):
        # Validate input
        validation_error = self.validate_input()
        if validation_error:
            return validation_error

        # Check if the username exists
        existing_user_error = self.check_existing_user()
        if existing_user_error:
            return existing_user_error

        # Hash the password and create a new user
        try:
            hashed_password = generate_password_hash(self.password)
            new_user = User(username=self.username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return {"message": "Registration successful!"}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": "An error occurred during registration", "details": str(e)}, 500
