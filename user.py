from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Numeric
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

# User Management Models
class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_type = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student_profile = db.relationship('Student', backref='user', uselist=False)
    teacher_profile = db.relationship('Teacher', backref='user', uselist=False)
    parent_profile = db.relationship('Parent', backref='user', uselist=False)
    staff_profile = db.relationship('Staff', backref='user', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role_type': self.role_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Student(db.Model):
    __tablename__ = 'students'
    
    student_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    admission_number = db.Column(db.String(50), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    address = db.Column(db.Text)
    emergency_contacts = db.Column(db.Text)  # JSON string
    medical_information = db.Column(db.Text)  # JSON string
    academic_status = db.Column(db.String(50), default='Active')
    enrollment_date = db.Column(db.Date, default=date.today)
    graduation_date = db.Column(db.Date)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    submissions = db.relationship('Submission', backref='student', lazy=True)
    grades = db.relationship('Grade', backref='student', lazy=True)
    report_cards = db.relationship('ReportCard', backref='student', lazy=True)
    invoices = db.relationship('Invoice', backref='student', lazy=True)
    payments = db.relationship('Payment', backref='student', lazy=True)
    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy=True)
    book_transactions = db.relationship('BookTransaction', backref='student', lazy=True)
    
    def get_emergency_contacts(self):
        return json.loads(self.emergency_contacts) if self.emergency_contacts else []
    
    def set_emergency_contacts(self, contacts):
        self.emergency_contacts = json.dumps(contacts)
    
    def get_medical_information(self):
        return json.loads(self.medical_information) if self.medical_information else {}
    
    def set_medical_information(self, info):
        self.medical_information = json.dumps(info)
    
    def to_dict(self):
        return {
            'student_id': self.student_id,
            'user_id': self.user_id,
            'admission_number': self.admission_number,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'address': self.address,
            'emergency_contacts': self.get_emergency_contacts(),
            'medical_information': self.get_medical_information(),
            'academic_status': self.academic_status,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'graduation_date': self.graduation_date.isoformat() if self.graduation_date else None
        }

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    teacher_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    qualifications = db.Column(db.Text)  # JSON string
    subjects_taught = db.Column(db.Text)  # JSON string
    hire_date = db.Column(db.Date)
    department = db.Column(db.String(100))
    performance_metrics = db.Column(db.Text)  # JSON string
    salary = db.Column(Numeric(10, 2))
    employment_status = db.Column(db.String(50), default='Active')
    
    # Relationships
    classes = db.relationship('Class', backref='teacher', lazy=True)
    assignments = db.relationship('Assignment', backref='teacher', lazy=True)
    grades = db.relationship('Grade', backref='teacher', lazy=True)
    
    def get_qualifications(self):
        return json.loads(self.qualifications) if self.qualifications else []
    
    def set_qualifications(self, quals):
        self.qualifications = json.dumps(quals)
    
    def get_subjects_taught(self):
        return json.loads(self.subjects_taught) if self.subjects_taught else []
    
    def set_subjects_taught(self, subjects):
        self.subjects_taught = json.dumps(subjects)
    
    def to_dict(self):
        return {
            'teacher_id': self.teacher_id,
            'user_id': self.user_id,
            'employee_id': self.employee_id,
            'qualifications': self.get_qualifications(),
            'subjects_taught': self.get_subjects_taught(),
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'department': self.department,
            'salary': float(self.salary) if self.salary else None,
            'employment_status': self.employment_status
        }

class Parent(db.Model):
    __tablename__ = 'parents'
    
    parent_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    relationship_type = db.Column(db.String(50))  # Father, Mother, Guardian, etc.
    contact_preferences = db.Column(db.Text)  # JSON string
    primary_contact = db.Column(db.Boolean, default=False)
    occupation = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    def get_contact_preferences(self):
        return json.loads(self.contact_preferences) if self.contact_preferences else {}
    
    def set_contact_preferences(self, prefs):
        self.contact_preferences = json.dumps(prefs)
    
    def to_dict(self):
        return {
            'parent_id': self.parent_id,
            'user_id': self.user_id,
            'relationship_type': self.relationship_type,
            'contact_preferences': self.get_contact_preferences(),
            'primary_contact': self.primary_contact,
            'occupation': self.occupation,
            'notes': self.notes
        }

class Staff(db.Model):
    __tablename__ = 'staff'
    
    staff_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    hire_date = db.Column(db.Date)
    salary = db.Column(Numeric(10, 2))
    employment_status = db.Column(db.String(50), default='Active')
    
    # Relationships
    staff_attendance = db.relationship('StaffAttendance', backref='staff', lazy=True)
    
    def to_dict(self):
        return {
            'staff_id': self.staff_id,
            'user_id': self.user_id,
            'employee_id': self.employee_id,
            'department': self.department,
            'position': self.position,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'salary': float(self.salary) if self.salary else None,
            'employment_status': self.employment_status
        }

# Academic Structure Models
class School(db.Model):
    __tablename__ = 'schools'
    
    school_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    configuration = db.Column(db.Text)  # JSON string
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    academic_years = db.relationship('AcademicYear', backref='school', lazy=True)
    classes = db.relationship('Class', backref='school', lazy=True)
    subjects = db.relationship('Subject', backref='school', lazy=True)
    fee_structures = db.relationship('FeeStructure', backref='school', lazy=True)
    financial_accounts = db.relationship('FinancialAccount', backref='school', lazy=True)
    announcements = db.relationship('Announcement', backref='school', lazy=True)
    library_books = db.relationship('LibraryBook', backref='school', lazy=True)
    inventory_items = db.relationship('InventoryItem', backref='school', lazy=True)
    
    def get_configuration(self):
        return json.loads(self.configuration) if self.configuration else {}
    
    def set_configuration(self, config):
        self.configuration = json.dumps(config)
    
    def to_dict(self):
        return {
            'school_id': self.school_id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'configuration': self.get_configuration(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AcademicYear(db.Model):
    __tablename__ = 'academic_years'
    
    year_id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.school_id'), nullable=False)
    year_name = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    term_structure = db.Column(db.Text)  # JSON string
    is_current = db.Column(db.Boolean, default=False)
    holiday_calendar = db.Column(db.Text)  # JSON string
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='academic_year', lazy=True)
    report_cards = db.relationship('ReportCard', backref='academic_year', lazy=True)
    fee_structures = db.relationship('FeeStructure', backref='academic_year', lazy=True)
    
    def get_term_structure(self):
        return json.loads(self.term_structure) if self.term_structure else []
    
    def set_term_structure(self, terms):
        self.term_structure = json.dumps(terms)
    
    def get_holiday_calendar(self):
        return json.loads(self.holiday_calendar) if self.holiday_calendar else []
    
    def set_holiday_calendar(self, holidays):
        self.holiday_calendar = json.dumps(holidays)
    
    def to_dict(self):
        return {
            'year_id': self.year_id,
            'school_id': self.school_id,
            'year_name': self.year_name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'term_structure': self.get_term_structure(),
            'is_current': self.is_current,
            'holiday_calendar': self.get_holiday_calendar()
        }

class Class(db.Model):
    __tablename__ = 'classes'
    
    class_id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.school_id'), nullable=False)
    year_id = db.Column(db.Integer, db.ForeignKey('academic_years.year_id'), nullable=False)
    class_name = db.Column(db.String(100), nullable=False)
    grade_level = db.Column(db.String(20))
    capacity = db.Column(db.Integer)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'))
    classroom = db.Column(db.String(50))
    schedule = db.Column(db.Text)  # JSON string
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='enrolled_class', lazy=True)
    assignments = db.relationship('Assignment', backref='assigned_class', lazy=True)
    attendance_records = db.relationship('AttendanceRecord', backref='attendance_class', lazy=True)
    
    def get_schedule(self):
        return json.loads(self.schedule) if self.schedule else {}
    
    def set_schedule(self, sched):
        self.schedule = json.dumps(sched)
    
    def to_dict(self):
        return {
            'class_id': self.class_id,
            'school_id': self.school_id,
            'year_id': self.year_id,
            'class_name': self.class_name,
            'grade_level': self.grade_level,
            'capacity': self.capacity,
            'teacher_id': self.teacher_id,
            'classroom': self.classroom,
            'schedule': self.get_schedule(),
            'is_active': self.is_active
        }

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    subject_id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.school_id'), nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)
    subject_code = db.Column(db.String(20))
    description = db.Column(db.Text)
    credit_hours = db.Column(db.Integer)
    prerequisites = db.Column(db.Text)  # JSON string
    learning_objectives = db.Column(db.Text)  # JSON string
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    assignments = db.relationship('Assignment', backref='subject', lazy=True)
    
    def get_prerequisites(self):
        return json.loads(self.prerequisites) if self.prerequisites else []
    
    def set_prerequisites(self, prereqs):
        self.prerequisites = json.dumps(prereqs)
    
    def get_learning_objectives(self):
        return json.loads(self.learning_objectives) if self.learning_objectives else []
    
    def set_learning_objectives(self, objectives):
        self.learning_objectives = json.dumps(objectives)
    
    def to_dict(self):
        return {
            'subject_id': self.subject_id,
            'school_id': self.school_id,
            'subject_name': self.subject_name,
            'subject_code': self.subject_code,
            'description': self.description,
            'credit_hours': self.credit_hours,
            'prerequisites': self.get_prerequisites(),
            'learning_objectives': self.get_learning_objectives(),
            'is_active': self.is_active
        }

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    enrollment_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=False)
    year_id = db.Column(db.Integer, db.ForeignKey('academic_years.year_id'), nullable=False)
    enrollment_date = db.Column(db.Date, default=date.today)
    status = db.Column(db.String(50), default='Active')
    completion_date = db.Column(db.Date)
    performance_summary = db.Column(db.Text)  # JSON string
    
    def get_performance_summary(self):
        return json.loads(self.performance_summary) if self.performance_summary else {}
    
    def set_performance_summary(self, summary):
        self.performance_summary = json.dumps(summary)
    
    def to_dict(self):
        return {
            'enrollment_id': self.enrollment_id,
            'student_id': self.student_id,
            'class_id': self.class_id,
            'year_id': self.year_id,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'status': self.status,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'performance_summary': self.get_performance_summary()
        }

