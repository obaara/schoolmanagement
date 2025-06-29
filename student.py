from flask import Blueprint, request, jsonify
from datetime import datetime, date
from sqlalchemy import or_, and_

from src.models.user import db, User, Student, Enrollment, Class, AcademicYear
from src.models.assessment import Grade, Assignment, AttendanceRecord, ReportCard
from src.models.financial import Invoice, Payment
from src.routes.auth import token_required, role_required

student_bp = Blueprint('student', __name__)

@student_bp.route('/', methods=['GET'])
@token_required
@role_required(['admin', 'teacher', 'staff'])
def get_students():
    """Get list of students with filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search', '')
        class_id = request.args.get('class_id', type=int)
        academic_status = request.args.get('academic_status', '')
        
        # Build query
        query = Student.query.join(User)
        
        # Apply filters
        if search:
            query = query.filter(or_(
                User.username.contains(search),
                User.email.contains(search),
                Student.admission_number.contains(search)
            ))
        
        if class_id:
            query = query.join(Enrollment).filter(
                and_(Enrollment.class_id == class_id, Enrollment.status == 'Active')
            )
        
        if academic_status:
            query = query.filter(Student.academic_status == academic_status)
        
        # Execute query with pagination
        students = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Format response
        result = {
            'students': [
                {
                    **student.to_dict(),
                    'user': student.user.to_dict()
                } for student in students.items
            ],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': students.total,
                'pages': students.pages,
                'has_next': students.has_next,
                'has_prev': students.has_prev
            }
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>', methods=['GET'])
@token_required
def get_student(student_id):
    """Get specific student details"""
    try:
        # Check permissions
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        # Students can only view their own profile
        if current_user_role == 'student':
            student = Student.query.filter_by(user_id=current_user_id).first()
            if not student or student.student_id != student_id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user_role not in ['admin', 'teacher', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get additional information
        current_enrollment = Enrollment.query.filter_by(
            student_id=student_id, status='Active'
        ).first()
        
        recent_grades = Grade.query.filter_by(student_id=student_id)\
            .order_by(Grade.graded_at.desc()).limit(10).all()
        
        attendance_summary = db.session.query(
            AttendanceRecord.status,
            db.func.count(AttendanceRecord.attendance_id).label('count')
        ).filter_by(student_id=student_id)\
         .group_by(AttendanceRecord.status).all()
        
        result = {
            'student': student.to_dict(),
            'user': student.user.to_dict(),
            'current_enrollment': current_enrollment.to_dict() if current_enrollment else None,
            'recent_grades': [grade.to_dict() for grade in recent_grades],
            'attendance_summary': {status: count for status, count in attendance_summary}
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/', methods=['POST'])
@token_required
@role_required(['admin', 'staff'])
def create_student():
    """Create new student"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409
        
        # Create user account
        user = User(
            username=data['username'],
            email=data['email'],
            role_type='student'
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create student profile
        student = Student(
            user_id=user.user_id,
            admission_number=data.get('admission_number', f'STU{user.user_id:06d}'),
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None,
            gender=data.get('gender'),
            address=data.get('address'),
            academic_status=data.get('academic_status', 'Active')
        )
        
        # Set emergency contacts and medical information
        if data.get('emergency_contacts'):
            student.set_emergency_contacts(data['emergency_contacts'])
        if data.get('medical_information'):
            student.set_medical_information(data['medical_information'])
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({
            'message': 'Student created successfully',
            'student': student.to_dict(),
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>', methods=['PUT'])
@token_required
def update_student(student_id):
    """Update student information"""
    try:
        # Check permissions
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        # Students can only update their own profile (limited fields)
        if current_user_role == 'student':
            student = Student.query.filter_by(user_id=current_user_id).first()
            if not student or student.student_id != student_id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user_role not in ['admin', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields based on user role
        if current_user_role in ['admin', 'staff']:
            # Admin/staff can update all fields
            if 'admission_number' in data:
                student.admission_number = data['admission_number']
            if 'date_of_birth' in data:
                student.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            if 'gender' in data:
                student.gender = data['gender']
            if 'address' in data:
                student.address = data['address']
            if 'academic_status' in data:
                student.academic_status = data['academic_status']
            if 'emergency_contacts' in data:
                student.set_emergency_contacts(data['emergency_contacts'])
            if 'medical_information' in data:
                student.set_medical_information(data['medical_information'])
        else:
            # Students can only update limited fields
            if 'address' in data:
                student.address = data['address']
            if 'emergency_contacts' in data:
                student.set_emergency_contacts(data['emergency_contacts'])
        
        # Update user information if provided
        if 'email' in data and current_user_role in ['admin', 'staff']:
            student.user.email = data['email']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Student updated successfully',
            'student': student.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>/enrollments', methods=['GET'])
@token_required
def get_student_enrollments(student_id):
    """Get student enrollment history"""
    try:
        # Check permissions
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        if current_user_role == 'student':
            student = Student.query.filter_by(user_id=current_user_id).first()
            if not student or student.student_id != student_id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user_role not in ['admin', 'teacher', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        enrollments = Enrollment.query.filter_by(student_id=student_id)\
            .join(Class).join(AcademicYear)\
            .order_by(AcademicYear.start_date.desc()).all()
        
        result = []
        for enrollment in enrollments:
            enrollment_data = enrollment.to_dict()
            enrollment_data['class'] = enrollment.enrolled_class.to_dict()
            enrollment_data['academic_year'] = enrollment.academic_year.to_dict()
            result.append(enrollment_data)
        
        return jsonify({'enrollments': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>/grades', methods=['GET'])
@token_required
def get_student_grades(student_id):
    """Get student grades"""
    try:
        # Check permissions
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        if current_user_role == 'student':
            student = Student.query.filter_by(user_id=current_user_id).first()
            if not student or student.student_id != student_id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user_role not in ['admin', 'teacher', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get query parameters
        subject_id = request.args.get('subject_id', type=int)
        assignment_type = request.args.get('assignment_type')
        
        # Build query
        query = Grade.query.filter_by(student_id=student_id)\
            .join(Assignment)
        
        if subject_id:
            query = query.filter(Assignment.subject_id == subject_id)
        
        if assignment_type:
            query = query.filter(Assignment.assignment_type == assignment_type)
        
        grades = query.order_by(Grade.graded_at.desc()).all()
        
        result = []
        for grade in grades:
            grade_data = grade.to_dict()
            grade_data['assignment'] = grade.assignment.to_dict()
            result.append(grade_data)
        
        return jsonify({'grades': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>/attendance', methods=['GET'])
@token_required
def get_student_attendance(student_id):
    """Get student attendance records"""
    try:
        # Check permissions
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        if current_user_role == 'student':
            student = Student.query.filter_by(user_id=current_user_id).first()
            if not student or student.student_id != student_id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user_role not in ['admin', 'teacher', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = AttendanceRecord.query.filter_by(student_id=student_id)
        
        if start_date:
            query = query.filter(AttendanceRecord.attendance_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        
        if end_date:
            query = query.filter(AttendanceRecord.attendance_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        attendance_records = query.order_by(AttendanceRecord.attendance_date.desc()).all()
        
        return jsonify({
            'attendance_records': [record.to_dict() for record in attendance_records]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>/financial', methods=['GET'])
@token_required
def get_student_financial(student_id):
    """Get student financial information"""
    try:
        # Check permissions
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        if current_user_role == 'student':
            student = Student.query.filter_by(user_id=current_user_id).first()
            if not student or student.student_id != student_id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user_role not in ['admin', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get invoices and payments
        invoices = Invoice.query.filter_by(student_id=student_id)\
            .order_by(Invoice.issue_date.desc()).all()
        
        payments = Payment.query.filter_by(student_id=student_id)\
            .order_by(Payment.payment_date.desc()).all()
        
        # Calculate totals
        total_invoiced = sum(float(invoice.total_amount) for invoice in invoices)
        total_paid = sum(float(payment.amount) for payment in payments if payment.status == 'Completed')
        outstanding_balance = total_invoiced - total_paid
        
        return jsonify({
            'invoices': [invoice.to_dict() for invoice in invoices],
            'payments': [payment.to_dict() for payment in payments],
            'summary': {
                'total_invoiced': total_invoiced,
                'total_paid': total_paid,
                'outstanding_balance': outstanding_balance
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>/report-cards', methods=['GET'])
@token_required
def get_student_report_cards(student_id):
    """Get student report cards"""
    try:
        # Check permissions
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        if current_user_role == 'student':
            student = Student.query.filter_by(user_id=current_user_id).first()
            if not student or student.student_id != student_id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user_role not in ['admin', 'teacher', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        report_cards = ReportCard.query.filter_by(student_id=student_id)\
            .join(AcademicYear)\
            .order_by(AcademicYear.start_date.desc(), ReportCard.term.desc()).all()
        
        result = []
        for report_card in report_cards:
            report_data = report_card.to_dict()
            report_data['academic_year'] = report_card.academic_year.to_dict()
            result.append(report_data)
        
        return jsonify({'report_cards': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

