from flask import Blueprint, request, jsonify
from datetime import datetime, date
from sqlalchemy import or_, and_

from src.models.user import db, School, AcademicYear, Class, Subject, Enrollment, Student, Teacher
from src.models.assessment import Assignment, Grade, ReportCard
from src.routes.auth import token_required, role_required

academic_bp = Blueprint('academic', __name__)

# School Management
@academic_bp.route('/schools', methods=['GET'])
@token_required
@role_required(['admin', 'staff'])
def get_schools():
    """Get list of schools"""
    try:
        schools = School.query.filter_by(is_active=True).all()
        return jsonify({
            'schools': [school.to_dict() for school in schools]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@academic_bp.route('/schools', methods=['POST'])
@token_required
@role_required(['admin'])
def create_school():
    """Create new school"""
    try:
        data = request.get_json()
        
        required_fields = ['name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        school = School(
            name=data['name'],
            address=data.get('address'),
            phone=data.get('phone'),
            email=data.get('email')
        )
        
        if data.get('configuration'):
            school.set_configuration(data['configuration'])
        
        db.session.add(school)
        db.session.commit()
        
        return jsonify({
            'message': 'School created successfully',
            'school': school.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Academic Year Management
@academic_bp.route('/academic-years', methods=['GET'])
@token_required
def get_academic_years():
    """Get list of academic years"""
    try:
        school_id = request.args.get('school_id', type=int)
        
        query = AcademicYear.query
        if school_id:
            query = query.filter_by(school_id=school_id)
        
        academic_years = query.order_by(AcademicYear.start_date.desc()).all()
        
        return jsonify({
            'academic_years': [year.to_dict() for year in academic_years]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@academic_bp.route('/academic-years', methods=['POST'])
@token_required
@role_required(['admin', 'staff'])
def create_academic_year():
    """Create new academic year"""
    try:
        data = request.get_json()
        
        required_fields = ['school_id', 'year_name', 'start_date', 'end_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # If this is set as current, unset other current years for the same school
        if data.get('is_current', False):
            AcademicYear.query.filter_by(
                school_id=data['school_id'], is_current=True
            ).update({'is_current': False})
        
        academic_year = AcademicYear(
            school_id=data['school_id'],
            year_name=data['year_name'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
            is_current=data.get('is_current', False)
        )
        
        if data.get('term_structure'):
            academic_year.set_term_structure(data['term_structure'])
        
        if data.get('holiday_calendar'):
            academic_year.set_holiday_calendar(data['holiday_calendar'])
        
        db.session.add(academic_year)
        db.session.commit()
        
        return jsonify({
            'message': 'Academic year created successfully',
            'academic_year': academic_year.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Class Management
@academic_bp.route('/classes', methods=['GET'])
@token_required
def get_classes():
    """Get list of classes"""
    try:
        # Get query parameters
        school_id = request.args.get('school_id', type=int)
        year_id = request.args.get('year_id', type=int)
        teacher_id = request.args.get('teacher_id', type=int)
        grade_level = request.args.get('grade_level')
        
        query = Class.query.filter_by(is_active=True)
        
        if school_id:
            query = query.filter_by(school_id=school_id)
        
        if year_id:
            query = query.filter_by(year_id=year_id)
        
        if teacher_id:
            query = query.filter_by(teacher_id=teacher_id)
        
        if grade_level:
            query = query.filter_by(grade_level=grade_level)
        
        classes = query.all()
        
        result = []
        for cls in classes:
            class_data = cls.to_dict()
            # Get enrollment count
            enrollment_count = Enrollment.query.filter_by(
                class_id=cls.class_id, status='Active'
            ).count()
            class_data['enrollment_count'] = enrollment_count
            
            # Get teacher info if assigned
            if cls.teacher:
                class_data['teacher'] = {
                    'teacher_id': cls.teacher.teacher_id,
                    'name': cls.teacher.user.username,
                    'employee_id': cls.teacher.employee_id
                }
            
            result.append(class_data)
        
        return jsonify({'classes': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@academic_bp.route('/classes', methods=['POST'])
@token_required
@role_required(['admin', 'staff'])
def create_class():
    """Create new class"""
    try:
        data = request.get_json()
        
        required_fields = ['school_id', 'year_id', 'class_name', 'grade_level']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Verify teacher exists if provided
        if data.get('teacher_id'):
            teacher = Teacher.query.get(data['teacher_id'])
            if not teacher:
                return jsonify({'error': 'Teacher not found'}), 404
        
        class_obj = Class(
            school_id=data['school_id'],
            year_id=data['year_id'],
            class_name=data['class_name'],
            grade_level=data['grade_level'],
            capacity=data.get('capacity'),
            teacher_id=data.get('teacher_id'),
            classroom=data.get('classroom')
        )
        
        if data.get('schedule'):
            class_obj.set_schedule(data['schedule'])
        
        db.session.add(class_obj)
        db.session.commit()
        
        return jsonify({
            'message': 'Class created successfully',
            'class': class_obj.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@academic_bp.route('/classes/<int:class_id>', methods=['PUT'])
@token_required
@role_required(['admin', 'staff'])
def update_class(class_id):
    """Update class information"""
    try:
        class_obj = Class.query.get(class_id)
        if not class_obj:
            return jsonify({'error': 'Class not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'class_name' in data:
            class_obj.class_name = data['class_name']
        if 'grade_level' in data:
            class_obj.grade_level = data['grade_level']
        if 'capacity' in data:
            class_obj.capacity = data['capacity']
        if 'teacher_id' in data:
            if data['teacher_id']:
                teacher = Teacher.query.get(data['teacher_id'])
                if not teacher:
                    return jsonify({'error': 'Teacher not found'}), 404
            class_obj.teacher_id = data['teacher_id']
        if 'classroom' in data:
            class_obj.classroom = data['classroom']
        if 'schedule' in data:
            class_obj.set_schedule(data['schedule'])
        if 'is_active' in data:
            class_obj.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Class updated successfully',
            'class': class_obj.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@academic_bp.route('/classes/<int:class_id>/students', methods=['GET'])
@token_required
def get_class_students(class_id):
    """Get students enrolled in a class"""
    try:
        # Check permissions
        current_user_role = request.current_user.get('role_type')
        
        if current_user_role == 'teacher':
            # Verify teacher is assigned to this class
            teacher = Teacher.query.filter_by(user_id=request.current_user['user_id']).first()
            if not teacher:
                return jsonify({'error': 'Teacher profile not found'}), 404
            
            assigned_class = Class.query.filter_by(
                class_id=class_id, teacher_id=teacher.teacher_id
            ).first()
            if not assigned_class:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user_role not in ['admin', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get enrolled students
        enrollments = Enrollment.query.filter_by(
            class_id=class_id, status='Active'
        ).join(Student).join(Student.user).all()
        
        result = []
        for enrollment in enrollments:
            student_data = enrollment.student.to_dict()
            student_data['user'] = enrollment.student.user.to_dict()
            student_data['enrollment'] = enrollment.to_dict()
            result.append(student_data)
        
        return jsonify({'students': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Subject Management
@academic_bp.route('/subjects', methods=['GET'])
@token_required
def get_subjects():
    """Get list of subjects"""
    try:
        school_id = request.args.get('school_id', type=int)
        
        query = Subject.query.filter_by(is_active=True)
        if school_id:
            query = query.filter_by(school_id=school_id)
        
        subjects = query.all()
        
        return jsonify({
            'subjects': [subject.to_dict() for subject in subjects]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@academic_bp.route('/subjects', methods=['POST'])
@token_required
@role_required(['admin', 'staff'])
def create_subject():
    """Create new subject"""
    try:
        data = request.get_json()
        
        required_fields = ['school_id', 'subject_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        subject = Subject(
            school_id=data['school_id'],
            subject_name=data['subject_name'],
            subject_code=data.get('subject_code'),
            description=data.get('description'),
            credit_hours=data.get('credit_hours')
        )
        
        if data.get('prerequisites'):
            subject.set_prerequisites(data['prerequisites'])
        
        if data.get('learning_objectives'):
            subject.set_learning_objectives(data['learning_objectives'])
        
        db.session.add(subject)
        db.session.commit()
        
        return jsonify({
            'message': 'Subject created successfully',
            'subject': subject.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Enrollment Management
@academic_bp.route('/enrollments', methods=['GET'])
@token_required
@role_required(['admin', 'staff'])
def get_enrollments():
    """Get list of enrollments"""
    try:
        # Get query parameters
        student_id = request.args.get('student_id', type=int)
        class_id = request.args.get('class_id', type=int)
        year_id = request.args.get('year_id', type=int)
        status = request.args.get('status')
        
        query = Enrollment.query
        
        if student_id:
            query = query.filter_by(student_id=student_id)
        
        if class_id:
            query = query.filter_by(class_id=class_id)
        
        if year_id:
            query = query.filter_by(year_id=year_id)
        
        if status:
            query = query.filter_by(status=status)
        
        enrollments = query.order_by(Enrollment.enrollment_date.desc()).all()
        
        result = []
        for enrollment in enrollments:
            enrollment_data = enrollment.to_dict()
            enrollment_data['student'] = enrollment.student.to_dict()
            enrollment_data['class'] = enrollment.enrolled_class.to_dict()
            enrollment_data['academic_year'] = enrollment.academic_year.to_dict()
            result.append(enrollment_data)
        
        return jsonify({'enrollments': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@academic_bp.route('/enrollments', methods=['POST'])
@token_required
@role_required(['admin', 'staff'])
def create_enrollment():
    """Enroll student in class"""
    try:
        data = request.get_json()
        
        required_fields = ['student_id', 'class_id', 'year_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if student is already enrolled in this class for this year
        existing_enrollment = Enrollment.query.filter_by(
            student_id=data['student_id'],
            class_id=data['class_id'],
            year_id=data['year_id'],
            status='Active'
        ).first()
        
        if existing_enrollment:
            return jsonify({'error': 'Student already enrolled in this class'}), 409
        
        # Check class capacity
        class_obj = Class.query.get(data['class_id'])
        if class_obj and class_obj.capacity:
            current_enrollment_count = Enrollment.query.filter_by(
                class_id=data['class_id'], status='Active'
            ).count()
            
            if current_enrollment_count >= class_obj.capacity:
                return jsonify({'error': 'Class is at full capacity'}), 400
        
        enrollment = Enrollment(
            student_id=data['student_id'],
            class_id=data['class_id'],
            year_id=data['year_id'],
            enrollment_date=datetime.strptime(data['enrollment_date'], '%Y-%m-%d').date() if data.get('enrollment_date') else date.today(),
            status=data.get('status', 'Active')
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify({
            'message': 'Student enrolled successfully',
            'enrollment': enrollment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@academic_bp.route('/enrollments/<int:enrollment_id>', methods=['PUT'])
@token_required
@role_required(['admin', 'staff'])
def update_enrollment(enrollment_id):
    """Update enrollment status"""
    try:
        enrollment = Enrollment.query.get(enrollment_id)
        if not enrollment:
            return jsonify({'error': 'Enrollment not found'}), 404
        
        data = request.get_json()
        
        if 'status' in data:
            enrollment.status = data['status']
        
        if 'completion_date' in data:
            enrollment.completion_date = datetime.strptime(data['completion_date'], '%Y-%m-%d').date()
        
        if 'performance_summary' in data:
            enrollment.set_performance_summary(data['performance_summary'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Enrollment updated successfully',
            'enrollment': enrollment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Assignment Management
@academic_bp.route('/assignments', methods=['GET'])
@token_required
def get_assignments():
    """Get list of assignments"""
    try:
        # Get query parameters
        class_id = request.args.get('class_id', type=int)
        subject_id = request.args.get('subject_id', type=int)
        teacher_id = request.args.get('teacher_id', type=int)
        assignment_type = request.args.get('assignment_type')
        is_published = request.args.get('is_published', type=bool)
        
        query = Assignment.query
        
        if class_id:
            query = query.filter_by(class_id=class_id)
        
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        
        if teacher_id:
            query = query.filter_by(teacher_id=teacher_id)
        
        if assignment_type:
            query = query.filter_by(assignment_type=assignment_type)
        
        if is_published is not None:
            query = query.filter_by(is_published=is_published)
        
        assignments = query.order_by(Assignment.created_at.desc()).all()
        
        result = []
        for assignment in assignments:
            assignment_data = assignment.to_dict()
            assignment_data['class'] = assignment.assigned_class.to_dict()
            assignment_data['subject'] = assignment.subject.to_dict()
            assignment_data['teacher'] = {
                'teacher_id': assignment.teacher.teacher_id,
                'name': assignment.teacher.user.username
            }
            result.append(assignment_data)
        
        return jsonify({'assignments': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

