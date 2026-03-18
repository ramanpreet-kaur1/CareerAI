from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User account model with authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    assessments = db.relationship('Assessment', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Assessment(db.Model):
    """Career assessment responses and results"""
    __tablename__ = 'assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Assessment status
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed
    progress = db.Column(db.Integer, default=0)  # 0-100%
    
    # Question responses (stored as JSON-like text)
    q1_interests = db.Column(db.Text)  # RIASEC activities
    q2_environment = db.Column(db.String(100))
    q3_technical_skill = db.Column(db.Integer)
    q3_communication_skill = db.Column(db.Integer)
    q3_math_skill = db.Column(db.Integer)
    q3_creative_skill = db.Column(db.Integer)
    q3_leadership_skill = db.Column(db.Integer)
    q3_detail_skill = db.Column(db.Integer)
    q4_academic_subjects = db.Column(db.String(200))
    q5_underutilized_skills = db.Column(db.Text)
    q6_success_definition = db.Column(db.String(200))
    q7_motivation = db.Column(db.String(200))
    q8_handle_setbacks = db.Column(db.String(200))
    q9_priorities = db.Column(db.Text)  # Ranked list
    q10_work_life_balance = db.Column(db.Integer)  # 1-10 scale
    q11_mentorship = db.Column(db.String(50))
    q12_education_level = db.Column(db.String(100))
    q13_additional_education = db.Column(db.String(100))
    q14_career_aspirations = db.Column(db.Text)
    q15_transition_timeline = db.Column(db.String(100))
    
    results = db.Column(db.Text)  # Complete AI analysis as JSON

    # AI Results
    ai_response = db.Column(db.Text)  # Full AI recommendation
    career_matches = db.Column(db.Text)  # JSON string of career options
    skill_roadmap = db.Column(db.Text)  # JSON string of learning path
    recommended_courses = db.Column(db.Text)  # JSON string of courses
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Assessment {self.id} - User {self.user_id}>'


class ChatHistory(db.Model):
    """Store follow-up chat conversations"""
    __tablename__ = 'chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatHistory {self.id}>'


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database initialized successfully!")
        print(f"📁 Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")


def get_user_by_email(email):
    """Fetch user by email"""
    return User.query.filter_by(email=email).first()


def get_user_by_username(username):
    """Fetch user by username"""
    return User.query.filter_by(username=username).first()


def create_user(username, email, password):
    """Create new user account"""
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def get_or_create_assessment(user_id):
    """Get user's latest assessment or create new one"""
    assessment = Assessment.query.filter_by(
        user_id=user_id, 
        status='in_progress'
    ).first()
    
    if not assessment:
        assessment = Assessment(user_id=user_id)
        db.session.add(assessment)
        db.session.commit()
    
    return assessment


def save_assessment_progress(assessment_id, question_data, progress_percent):
    """Save assessment answers incrementally"""
    assessment = Assessment.query.get(assessment_id)
    
    if assessment:
        # Update fields based on question_data dictionary
        for key, value in question_data.items():
            if hasattr(assessment, key):
                setattr(assessment, key, value)
        
        assessment.progress = progress_percent
        assessment.last_updated = datetime.utcnow()
        db.session.commit()
    
    return assessment


def complete_assessment(assessment_id, ai_results):
    """Mark assessment as complete and save AI results"""
    assessment = Assessment.query.get(assessment_id)
    
    if assessment:
        assessment.status = 'completed'
        assessment.progress = 100
        assessment.completed_at = datetime.utcnow()
        assessment.ai_response = ai_results.get('full_response', '')
        assessment.career_matches = ai_results.get('career_matches', '')
        assessment.skill_roadmap = ai_results.get('skill_roadmap', '')
        assessment.recommended_courses = ai_results.get('courses', '')
        db.session.commit()
    
    return assessment


def get_user_assessments(user_id):
    """Get all completed assessments for a user"""
    return Assessment.query.filter_by(
        user_id=user_id, 
        status='completed'
    ).order_by(Assessment.completed_at.desc()).all()


def get_all_assessments_admin():
    """Admin view: Get all assessments"""
    return Assessment.query.order_by(Assessment.created_at.desc()).all()
