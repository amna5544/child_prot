# models/model.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ChildRegistration(db.Model):
    __tablename__ = 'child_registration'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    child_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    admission_date = db.Column(db.Date, nullable=False)
    admission_location = db.Column(db.String(100), nullable=False)
    child_photo = db.Column(db.String(255), nullable=False)
    photo_path = db.Column(db.String(255), nullable=False)

    # Relationships
    case_histories = db.relationship(
        'CaseHistory',
        backref='child',
        cascade="all, delete",
        lazy=True
    )
    counselling_sessions = db.relationship(
        'CounsellingSessions',
        backref='child',
        cascade="all, delete",
        lazy=True
    )
    initial_assessments = db.relationship(
        'InitialAssessment',
        backref='child',
        cascade="all, delete",
        lazy=True
    )

class CaseHistory(db.Model):
    __tablename__ = 'case_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    child_id = db.Column(
        db.Integer,
        db.ForeignKey('child_registration.id', ondelete='CASCADE'),
        nullable=False
    )
    name = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    admission_source = db.Column(db.String(255), nullable=False)
    abuse_status = db.Column(db.String(100), nullable=False)
    family_history = db.Column(db.Text, nullable=False)
    medical_history = db.Column(db.Text, nullable=False)
    psychological_history = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False
    )

class CounsellingSessions(db.Model):
    __tablename__ = 'counselling_sessions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    child_id = db.Column(
        db.Integer,
        db.ForeignKey('child_registration.id', ondelete='CASCADE'),
        nullable=False
    )
    counsellor_name = db.Column(db.String(255), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    session_notes = db.Column(db.Text, nullable=False)
    outcomes = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False
    )

class CpiVisits(db.Model):
    __tablename__ = 'cpi_visits'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    visit_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False
    )

class CspVisits(db.Model):
    __tablename__ = 'csp_visits'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    visit_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False
    )

class FamilyCounselling(db.Model):
    __tablename__ = 'family_counselling'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    family_name = db.Column(db.String(255), nullable=False)
    father_name = db.Column(db.String(255), nullable=False)
    mother_name = db.Column(db.String(255), nullable=False)
    session_details = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False
    )

class GroupSessions(db.Model):
    __tablename__ = 'group_sessions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    child_one_name = db.Column(db.String(255), nullable=False)
    child_two_name = db.Column(db.String(255))
    child_three_name = db.Column(db.String(255))
    child_four_name = db.Column(db.String(255))
    session_details = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False
    )

class IndividualSessions(db.Model):
    __tablename__ = 'individual_sessions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_name = db.Column(db.String(255), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    session_details = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False
    )

class InitialAssessment(db.Model):
    __tablename__ = 'initial_assessment'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    child_id = db.Column(
        db.Integer,
        db.ForeignKey('child_registration.id', ondelete='CASCADE'),
        nullable=False
    )
    registration_no = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    religion = db.Column(db.String(100), nullable=False)
    education = db.Column(db.String(255), nullable=False)
    birth_order = db.Column(db.String(50), nullable=False)
    repeater = db.Column(db.String(50), nullable=False)
    occupation = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(255), nullable=False)
    father_occupation = db.Column(db.String(255), nullable=False)
    mother_name = db.Column(db.String(255), nullable=False)
    mother_occupation = db.Column(db.String(255), nullable=False)
    siblings_count = db.Column(db.Integer, nullable=False)
    siblings_details = db.Column(db.Text, nullable=False)
    relations_with_parents = db.Column(db.Text, nullable=False)
    home_address = db.Column(db.String(255), nullable=False)
    contact_no = db.Column(db.String(20), nullable=False)
    abuse_history = db.Column(db.Text, nullable=False)
    significant_complaint = db.Column(db.Text, nullable=False)
    work_history = db.Column(db.Text, nullable=False)
    remarks = db.Column(db.Text, nullable=False)
    forward_to = db.Column(db.String(255))
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False
    )

class StaffCounselling(db.Model):
    __tablename__ = 'staff_counselling'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    staff_role = db.Column(db.String(50), nullable=False)
    session_activity = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False
    )

class Users(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Add this column (e.g., 'admin' or 'user')
