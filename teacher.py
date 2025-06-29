from flask import Blueprint, request, jsonify
from datetime import datetime, date
from sqlalchemy import or_, and_

from src.models.user import db, User, Teacher, Class, Subject
from src.models.assessment import Assignment, Grade, AttendanceRecord
from src.routes.auth import token_required, role_required

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/', methods=['GET'])
@token_required
@role_required(['admin', 'staff'])
def get_teachers():
    """Get list of teachers with filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search', '')
        department = request.args.get('department', '')
        employment_status = request.args.get('employment_status', '')
        
        # Build query
        query = Teacher.query.join(User)
        
        # Apply filters
        if search:
            query = query.filter(or_(
                User.username.contains(search),
                User.email.contains(search),
                Teacher.employee_id.contains(search)
            ))
        
        if department:
            query = query.filter(Teacher.department == department)
        
        if employment_status:
            query = query.filter(Teacher.employment_status == employment_status)
        
        # Execute query with pagination
        teachers = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Format response
        result = {
            'teachers': [
                {
                    **teacher.to_dict(),
                    'user': teacher.user.to_dict()
                } for teacher in teachers.items
            ],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': teachers.total,
                'pages': teachers.pages,
                'has_next': teachers.has_next,
                'has_prev': teachers.has_prev
            }
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@teacher_bp.route('/<int:teacher_id>', methods=['GET'])
@token_required
def get_teacher(teacher_id):
    """Get specific teacher details"""
    try:
        # Check permissions
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        # Teachers can only view their own profile
        if current_user_role == 'teacher':
            teacher = Teacher.query.filter_by(user_id=current_user_id).first()
            if not teacher or teacher.teacher_id != teacher_id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user_role not in ['admin', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        
        # Get additional information
        assigned_classes = Class.query.filter_by(teacher_id=teacher_id).all()
        recent_assignments = Assignment.query.filter_by(teacher_id=teacher_id)\
            .order_by(Assignment.created_at.desc()).limit(10).all()
        
        result = {
            'teacher': teacher.to_dict(),
            'user': teacher.user.to_dict(),
            'assigned_classes': [cls.to_dict() for cls in assigned_classes],
            'recent_assignments': [assignment.to_dict() for assignment in recent_assignments]
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@teacher_bp.route('/', methods=['POST'])
@token_required
@role_required(['admin', 'staff'])
def create_teacher():
    """Create new teacher"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'employee_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409
        
        # Check if employee ID already exists
        existing_teacher = Teacher.query.filter_by(employee_id=data['employee_id']).first()
        if existing_teacher:
            return jsonify({'error': 'Employee ID already exists'}), 409
        
        # Create user account
        user = User(
            username=data['username'],
            email=data['email'],
            role_type='teacher'
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create teacher profile
        teacher = Teacher(
            user_id=user.user_id,
            employee_id=data['employee_id'],
            hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d').date() if data.get('hire_date') else None,
            department=data.get('department'),
            salary=data.get('salary'),
            employment_status=data.get('employment_status', 'Active')
        )
        
        # Set qualifications and subjects taught
        if data.get('qualifications'):
            teacher.set_qualifications(data['qualifications'])
        if data.get('subjects_taught'):
            teacher.set_subjects_taught(data['subjects_taught'])
        
        db.session.add(teacher)
        db.session.commit()
        
        return jsonify({
            'message': 'Teacher created successfully',
            'teacher': teacher.to_dict(),
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@teacher_bp.route('/<int:teacher_id>', methods=['PUT'])
@token_required
def update_teacher(teacher_id):
    """Update teacher information"""
    try:
        # Check permissions
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        # Teachers can only update their own profile (limited fields)
        if current_user_role == 'teacher':
            teacher = Teacher.query.filter_by(user_id=current_user_id).first()
            if not teacher or teacher.teacher_id != teacher_id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user_role not in ['admin', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields based on user role
        if current_user_role in ['admin', 'staff']:
            # Admin/staff can update all fields
            if 'employee_id' in data:
                # Check if new employee ID already exists
                existing_teacher = Teacher.query.filter(
                    and_(Teacher.employee_id == data['employee_id'], 
                         Teacher.teacher_id != teacher_id)
                ).first()
                if existing_teacher:
                    return jsonify({'error': 'Employee ID already exists'}), 409
                teacher.employee_id = data['employee_id']
            
            if 'hire_date' in data:
                teacher.hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
            if 'department' in data:
                teacher.department = data['department']
            if 'salary' in data:
                teacher.salary = data['salary']
            if 'employment_status' in data:
                teacher.employment_status = data['employment_status']
            if 'qualifications' in data:
                teacher.set_qualifications(data['qualifications'])
            if 'subjects_taught' in data:
                teacher.set_subjects_taught(data['subjects_taught'])
        else:
            # Teachers can only update limited fields
            if 'qualifications' in data:
                teacher.set_qualifications(data['qualifications'])
        
        # Update user information if provided
        if 'email' in data and current_user_role in ['admin', 'staff']:
            teacher.user.email = data['email']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Teacher updated successfully',
            'teacher': teacher.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@teacher_bp.route('/<int:teacher_id>/classes', methods=['GET'])
@token_required
def get_teacher_classes(teacher_id):
    """Get classes assigned to teacher"""
    try:
        # Check permissions
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        if current_user_role == 'teacher':
            teacher = Teacher.query.filter_by(user_id=current_user_id).first()
            if not teacher or teacher.teacher_id != teacher_id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user_role not in ['admin', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        classes = Class.query.filter_by(teacher_id=teacher_id, is_active=True).all()
        
        result = []
        for cls in classes:
            class_data = cls.to_dict()
            # Get enrollment count
            from src.models.user import Enrollment
            enrollment_count = Enrollment.query.filter_by(
                class_id=cls.class_id, status='Active'
            ).count()
            class_data['enrollment_count'] = enrollment_count
            result.append(class_data)
        
        return jsonify({'classes': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@teacher_bp.route('/<int:teacher_id>/assignments', methods=['GET'])
@token_required
def get_teacher_assignments(teacher_id):
    """Get assignments created by teacher"""
    try:
        # Check permissions
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        if current_user_role == 'teacher':
            teacher = Teacher.query.filter_by(user_id=current_user_id).first()
            if not teacher or teacher.teacher_id != teacher_id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user_role not in ['admin', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get query parameters
        class_id = request.args.get('class_id', type=int)
        subject_id = request.args.get('subject_id', type=int)
        assignment_type = request.args.get('assignment_type')
        
        query = Assignment.query.filter_by(teacher_id=teacher_id)
        
        if class_id:
            query = query.filter(Assignment.class_id == class_id)
        
        if subject_id:
            query = query.filter(Assignment.subject_id == subject_id)
        
        if assignment_type:
            query = query.filter(Assignment.assignment_type == assignment_type)
        
        assignments = query.order_by(Assignment.created_at.desc()).all()
        
        result = []
        for assignment in assignments:
            assignment_data = assignment.to_dict()
            # Get submission count
            from src.models.assessment import Submission
            submission_count = Submission.query.filter_by(
                assignment_id=assignment.assignment_id
            ).count()
            assignment_data['submission_count'] = submission_count
            result.append(assignment_data)
        
        return jsonify({'assignments': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@teacher_bp.route('/<int:teacher_id>/assignments', methods=['POST'])
@token_required
def create_assignment(teacher_id):
    """Create new assignment"""
    try:
        # Check permissions
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        if current_user_role == 'teacher':
            teacher = Teacher.query.filter_by(user_id=current_user_id).first()
            if not teacher or teacher.teacher_id != teacher_id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user_role not in ['admin', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'class_id', 'subject_id', 'due_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Verify teacher has access to the class
        assigned_class = Class.query.filter_by(
            class_id=data['class_id'], teacher_id=teacher_id
        ).first()
        if not assigned_class:
            return jsonify({'error': 'Teacher not assigned to this class'}), 403
        
        # Create assignment
        assignment = Assignment(
            class_id=data['class_id'],
            subject_id=data['subject_id'],
            teacher_id=teacher_id,
            title=data['title'],
            description=data.get('description'),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date(),
            max_points=data.get('max_points'),
            weight_factor=data.get('weight_factor', 1.0),
            assignment_type=data.get('assignment_type', 'Assignment'),
            is_published=data.get('is_published', False)
        )
        
        if data.get('grading_criteria'):
            assignment.set_grading_criteria(data['grading_criteria'])
        
        db.session.add(assignment)
        db.session.commit()
        
        return jsonify({
            'message': 'Assignment created successfully',
            'assignment': assignment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@teacher_bp.route('/<int:teacher_id>/grades', methods=['GET'])
@token_required
def get_teacher_grades(teacher_id):
    """Get grades given by teacher"""
    try:
        # Check permissions
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        if current_user_role == 'teacher':
            teacher = Teacher.query.filter_by(user_id=current_user_id).first()
            if not teacher or teacher.teacher_id != teacher_id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user_role not in ['admin', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get query parameters
        assignment_id = request.args.get('assignment_id', type=int)
        student_id = request.args.get('student_id', type=int)
        
        query = Grade.query.filter_by(teacher_id=teacher_id)
        
        if assignment_id:
            query = query.filter(Grade.assignment_id == assignment_id)
        
        if student_id:
            query = query.filter(Grade.student_id == student_id)
        
        grades = query.order_by(Grade.graded_at.desc()).all()
        
        result = []
        for grade in grades:
            grade_data = grade.to_dict()
            grade_data['assignment'] = grade.assignment.to_dict()
            grade_data['student'] = grade.student.to_dict()
            result.append(grade_data)
        
        return jsonify({'grades': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@teacher_bp.route('/<int:teacher_id>/attendance', methods=['POST'])
@token_required
def record_attendance(teacher_id):
    """Record student attendance"""
    try:
        # Check permissions
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        if current_user_role == 'teacher':
            teacher = Teacher.query.filter_by(user_id=current_user_id).first()
            if not teacher or teacher.teacher_id != teacher_id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user_role not in ['admin', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['class_id', 'attendance_date', 'attendance_records']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Verify teacher has access to the class
        assigned_class = Class.query.filter_by(
            class_id=data['class_id'], teacher_id=teacher_id
        ).first()
        if not assigned_class:
            return jsonify({'error': 'Teacher not assigned to this class'}), 403
        
        attendance_date = datetime.strptime(data['attendance_date'], '%Y-%m-%d').date()
        
        # Process attendance records
        created_records = []
        for record_data in data['attendance_records']:
            # Check if attendance already exists for this date
            existing_record = AttendanceRecord.query.filter_by(
                student_id=record_data['student_id'],
                class_id=data['class_id'],
                attendance_date=attendance_date
            ).first()
            
            if existing_record:
                # Update existing record
                existing_record.status = record_data['status']
                existing_record.remarks = record_data.get('remarks')
                existing_record.recorded_by = current_user_id
                created_records.append(existing_record)
            else:
                # Create new record
                attendance_record = AttendanceRecord(
                    student_id=record_data['student_id'],
                    class_id=data['class_id'],
                    attendance_date=attendance_date,
                    status=record_data['status'],
                    remarks=record_data.get('remarks'),
                    recorded_by=current_user_id
                )
                db.session.add(attendance_record)
                created_records.append(attendance_record)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Attendance recorded successfully',
            'records': [record.to_dict() for record in created_records]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

