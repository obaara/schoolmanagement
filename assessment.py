from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Numeric
from datetime import datetime, date
import json

# Import db from user models
from src.models.user import db

# Assessment and Grading Models
class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    assignment_id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    max_points = db.Column(Numeric(5, 2))
    weight_factor = db.Column(Numeric(3, 2), default=1.0)
    assignment_type = db.Column(db.String(50))  # Homework, Quiz, Exam, Project, etc.
    grading_criteria = db.Column(db.Text)  # JSON string
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    submissions = db.relationship('Submission', backref='assignment', lazy=True)
    grades = db.relationship('Grade', backref='assignment', lazy=True)
    
    def get_grading_criteria(self):
        return json.loads(self.grading_criteria) if self.grading_criteria else {}
    
    def set_grading_criteria(self, criteria):
        self.grading_criteria = json.dumps(criteria)
    
    def to_dict(self):
        return {
            'assignment_id': self.assignment_id,
            'class_id': self.class_id,
            'subject_id': self.subject_id,
            'teacher_id': self.teacher_id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'max_points': float(self.max_points) if self.max_points else None,
            'weight_factor': float(self.weight_factor) if self.weight_factor else None,
            'assignment_type': self.assignment_type,
            'grading_criteria': self.get_grading_criteria(),
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Submission(db.Model):
    __tablename__ = 'submissions'
    
    submission_id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.assignment_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    submission_data = db.Column(db.Text)  # JSON string - file paths, text content, etc.
    status = db.Column(db.String(50), default='Submitted')  # Submitted, Graded, Late, etc.
    version_number = db.Column(db.Integer, default=1)
    feedback = db.Column(db.Text)  # JSON string
    
    def get_submission_data(self):
        return json.loads(self.submission_data) if self.submission_data else {}
    
    def set_submission_data(self, data):
        self.submission_data = json.dumps(data)
    
    def get_feedback(self):
        return json.loads(self.feedback) if self.feedback else {}
    
    def set_feedback(self, feedback_data):
        self.feedback = json.dumps(feedback_data)
    
    def to_dict(self):
        return {
            'submission_id': self.submission_id,
            'assignment_id': self.assignment_id,
            'student_id': self.student_id,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'submission_data': self.get_submission_data(),
            'status': self.status,
            'version_number': self.version_number,
            'feedback': self.get_feedback()
        }

class Grade(db.Model):
    __tablename__ = 'grades'
    
    grade_id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.assignment_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'), nullable=False)
    points_earned = db.Column(Numeric(5, 2))
    letter_grade = db.Column(db.String(5))
    comments = db.Column(db.Text)
    graded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_final = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'grade_id': self.grade_id,
            'assignment_id': self.assignment_id,
            'student_id': self.student_id,
            'teacher_id': self.teacher_id,
            'points_earned': float(self.points_earned) if self.points_earned else None,
            'letter_grade': self.letter_grade,
            'comments': self.comments,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None,
            'is_final': self.is_final
        }

class ReportCard(db.Model):
    __tablename__ = 'report_cards'
    
    report_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    year_id = db.Column(db.Integer, db.ForeignKey('academic_years.year_id'), nullable=False)
    term = db.Column(db.String(50), nullable=False)
    grade_summary = db.Column(db.Text)  # JSON string
    teacher_comments = db.Column(db.Text)
    principal_comments = db.Column(db.Text)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=False)
    
    def get_grade_summary(self):
        return json.loads(self.grade_summary) if self.grade_summary else {}
    
    def set_grade_summary(self, summary):
        self.grade_summary = json.dumps(summary)
    
    def to_dict(self):
        return {
            'report_id': self.report_id,
            'student_id': self.student_id,
            'year_id': self.year_id,
            'term': self.term,
            'grade_summary': self.get_grade_summary(),
            'teacher_comments': self.teacher_comments,
            'principal_comments': self.principal_comments,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'is_published': self.is_published
        }

# Attendance Models
class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    
    attendance_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # Present, Absent, Late, Excused
    check_in_time = db.Column(db.Time)
    check_out_time = db.Column(db.Time)
    remarks = db.Column(db.Text)
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'attendance_id': self.attendance_id,
            'student_id': self.student_id,
            'class_id': self.class_id,
            'attendance_date': self.attendance_date.isoformat() if self.attendance_date else None,
            'status': self.status,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'remarks': self.remarks,
            'recorded_by': self.recorded_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class StaffAttendance(db.Model):
    __tablename__ = 'staff_attendance'
    
    attendance_id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False)
    check_in_time = db.Column(db.Time)
    check_out_time = db.Column(db.Time)
    hours_worked = db.Column(Numeric(4, 2))
    status = db.Column(db.String(20), nullable=False)  # Present, Absent, Late, Half Day
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'attendance_id': self.attendance_id,
            'staff_id': self.staff_id,
            'attendance_date': self.attendance_date.isoformat() if self.attendance_date else None,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'hours_worked': float(self.hours_worked) if self.hours_worked else None,
            'status': self.status,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

