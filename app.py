import awsgi
# Existing imports...
from flask import Flask
from flask_cors import CORS
from flask_backend.Config import Config
from flask_backend.model import db, hash_existing_passwords
from flask_backend.routes import auth_bp

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure app from Config.py
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    with app.app_context():
        hash_existing_passwords()
    app.run(debug=True)

from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app)

# Lambda handler for AWS Lambda
def lambda_handler(event, context):
    return awsgi.response(app, event, context, base64_content_types={"image/png"})
