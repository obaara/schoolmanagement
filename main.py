import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS

# Import database and models
from src.models.user import db
from src.models.assessment import *
from src.models.financial import *
from src.models.administrative import *

# Import route blueprints
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.student import student_bp
from src.routes.teacher import teacher_bp
from src.routes.academic import academic_bp
from src.routes.financial import financial_bp
from src.routes.administrative import administrative_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'school_management_secret_key_2025'

# Enable CORS for all routes
CORS(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(student_bp, url_prefix='/api/students')
app.register_blueprint(teacher_bp, url_prefix='/api/teachers')
app.register_blueprint(academic_bp, url_prefix='/api/academic')
app.register_blueprint(financial_bp, url_prefix='/api/financial')
app.register_blueprint(administrative_bp, url_prefix='/api/admin')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create all database tables
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/api/health')
def health_check():
    return {'status': 'healthy', 'message': 'School Management System API is running'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

