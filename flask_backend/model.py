from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

# Define the User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

# Function to hash plaintext passwords in the database
def hash_existing_passwords():
    users = User.query.all()
    for user in users:
        # Check if the password is already hashed
        if len(user.password) < 20:  # Assuming hashed passwords are longer than 20 characters
            user.password = generate_password_hash(user.password)
            db.session.add(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error while hashing passwords: {str(e)}")
