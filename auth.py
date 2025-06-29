from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps
import os

from src.models.user import db, User, Student, Teacher, Parent, Staff

auth_bp = Blueprint('auth', __name__)

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'school_management_jwt_secret_2025')
JWT_EXPIRATION_HOURS = 24

def generate_token(user):
    """Generate JWT token for authenticated user"""
    payload = {
        'user_id': user.user_id,
        'username': user.username,
        'email': user.email,
        'role_type': user.role_type,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    """Verify JWT token and return user data"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Verify token
        payload = verify_token(token)
        if payload is None:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # Add user info to request context
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated

def role_required(allowed_roles):
    """Decorator to require specific user roles"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = request.current_user.get('role_type')
            if user_role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate token
        token = generate_token(user)
        
        # Get role-specific profile data
        profile_data = None
        if user.role_type == 'student' and user.student_profile:
            profile_data = user.student_profile.to_dict()
        elif user.role_type == 'teacher' and user.teacher_profile:
            profile_data = user.teacher_profile.to_dict()
        elif user.role_type == 'parent' and user.parent_profile:
            profile_data = user.parent_profile.to_dict()
        elif user.role_type == 'staff' and user.staff_profile:
            profile_data = user.staff_profile.to_dict()
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict(),
            'profile': profile_data,
            'expires_in': JWT_EXPIRATION_HOURS * 3600  # seconds
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'role_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409
        
        # Validate role type
        valid_roles = ['admin', 'teacher', 'student', 'parent', 'staff']
        if data['role_type'] not in valid_roles:
            return jsonify({'error': 'Invalid role type'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            role_type=data['role_type']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create role-specific profile
        if data['role_type'] == 'student':
            profile = Student(
                user_id=user.user_id,
                admission_number=data.get('admission_number', f'STU{user.user_id:06d}'),
                date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None,
                gender=data.get('gender'),
                address=data.get('address')
            )
            db.session.add(profile)
            
        elif data['role_type'] == 'teacher':
            profile = Teacher(
                user_id=user.user_id,
                employee_id=data.get('employee_id', f'TCH{user.user_id:06d}'),
                hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d').date() if data.get('hire_date') else None,
                department=data.get('department'),
                salary=data.get('salary')
            )
            if data.get('qualifications'):
                profile.set_qualifications(data['qualifications'])
            if data.get('subjects_taught'):
                profile.set_subjects_taught(data['subjects_taught'])
            db.session.add(profile)
            
        elif data['role_type'] == 'parent':
            profile = Parent(
                user_id=user.user_id,
                relationship_type=data.get('relationship_type', 'Parent'),
                primary_contact=data.get('primary_contact', True),
                occupation=data.get('occupation')
            )
            db.session.add(profile)
            
        elif data['role_type'] == 'staff':
            profile = Staff(
                user_id=user.user_id,
                employee_id=data.get('employee_id', f'STF{user.user_id:06d}'),
                department=data.get('department'),
                position=data.get('position'),
                hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d').date() if data.get('hire_date') else None,
                salary=data.get('salary')
            )
            db.session.add(profile)
        
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@token_required
def refresh_token():
    """Refresh JWT token"""
    try:
        user = User.query.get(request.current_user['user_id'])
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 404
        
        # Generate new token
        token = generate_token(user)
        
        return jsonify({
            'message': 'Token refreshed successfully',
            'token': token,
            'expires_in': JWT_EXPIRATION_HOURS * 3600
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """User logout endpoint"""
    # In a production system, you might want to blacklist the token
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get current user profile"""
    try:
        user = User.query.get(request.current_user['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get role-specific profile data
        profile_data = None
        if user.role_type == 'student' and user.student_profile:
            profile_data = user.student_profile.to_dict()
        elif user.role_type == 'teacher' and user.teacher_profile:
            profile_data = user.teacher_profile.to_dict()
        elif user.role_type == 'parent' and user.parent_profile:
            profile_data = user.parent_profile.to_dict()
        elif user.role_type == 'staff' and user.staff_profile:
            profile_data = user.staff_profile.to_dict()
        
        return jsonify({
            'user': user.to_dict(),
            'profile': profile_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        user = User.query.get(request.current_user['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Validate new password
        if len(data['new_password']) < 6:
            return jsonify({'error': 'New password must be at least 6 characters long'}), 400
        
        # Update password
        user.set_password(data['new_password'])
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token_endpoint():
    """Verify if token is valid"""
    return jsonify({
        'valid': True,
        'user': request.current_user
    }), 200

