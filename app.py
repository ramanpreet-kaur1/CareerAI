from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import config
from database import db, User, create_user, get_user_by_email, get_user_by_username, get_or_create_assessment, Assessment
from datetime import datetime
import os

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Create instance folder if it doesn't exist
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        print(f"✅ Created instance folder: {instance_path}")
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created!")
    
    # ============================================
    # ROUTES
    # ============================================
    
    @app.route('/')
    def index():
        """Landing page"""
        return render_template('index.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """User registration"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validation
            errors = []
            
            if len(username) < 3:
                errors.append('Username must be at least 3 characters long.')
            
            if len(password) < 6:
                errors.append('Password must be at least 6 characters long.')
            
            if password != confirm_password:
                errors.append('Passwords do not match.')
            
            if get_user_by_username(username):
                errors.append('Username already taken.')
            
            if get_user_by_email(email):
                errors.append('Email already registered.')
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('register.html')
            
            # Create user
            try:
                user = create_user(username, email, password)
                flash('Account created successfully! Please log in.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash(f'Error creating account: {str(e)}', 'error')
                return render_template('register.html')
        
        return render_template('register.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            remember = request.form.get('remember', False)
            
            user = get_user_by_email(email)
            
            if user and user.check_password(password):
                login_user(user, remember=remember)
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                flash(f'Welcome back, {user.username}!', 'success')
                
                # Redirect to next page or dashboard
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'error')
        
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        """User logout"""
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """User dashboard"""
        return render_template('dashboard.html')
    
    @app.route('/profile')
    @login_required
    def profile():
        """User profile page"""
        return render_template('profile.html')
    
    # ============================================
    # ASSESSMENT ROUTES (Phase 3)
    # ============================================
    
    @app.route('/assessment/start')
    @login_required
    def assessment_start():
        """Start or resume assessment"""
        assessment = get_or_create_assessment(current_user.id)
        return redirect(url_for('assessment_questions', assessment_id=assessment.id))
    
    @app.route('/assessment/<int:assessment_id>/questions', methods=['GET', 'POST'])
    @login_required
    def assessment_questions(assessment_id):
        """Show assessment questions"""
        assessment = Assessment.query.get_or_404(assessment_id)
        
        # Security check
        if assessment.user_id != current_user.id:
            flash('Unauthorized access.', 'error')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            # Save answers (Phase 4 will handle AI processing)
            try:
                # For now, just collect the data
                form_data = request.form.to_dict(flat=False)
                
                # Store answers in assessment
                assessment.q1_interests = ','.join(form_data.get('q1_interests', []))
                assessment.q2_environment = form_data.get('q2_environment', [''])[0]
                assessment.q3_technical_skill = form_data.get('q3_technical_skill', ['5'])[0]
                assessment.q3_communication_skill = form_data.get('q3_communication_skill', ['5'])[0]
                assessment.q3_math_skill = form_data.get('q3_math_skill', ['5'])[0]
                assessment.q3_creative_skill = form_data.get('q3_creative_skill', ['5'])[0]
                assessment.q3_leadership_skill = form_data.get('q3_leadership_skill', ['5'])[0]
                assessment.q3_detail_skill = form_data.get('q3_detail_skill', ['5'])[0]
                assessment.q4_academic_subjects = ','.join(form_data.get('q4_academic_subjects', []))
                assessment.q5_underutilized_skills = form_data.get('q5_underutilized_skills', [''])[0]
                assessment.q6_success_definition = form_data.get('q6_success_definition', [''])[0]
                assessment.q7_motivation = form_data.get('q7_motivation', [''])[0]
                assessment.q8_handle_setbacks = form_data.get('q8_handle_setbacks', [''])[0]
                assessment.q9_priorities = form_data.get('q9_priorities', [''])[0]
                assessment.q10_work_life_balance = form_data.get('q10_work_life_balance', ['5'])[0]
                assessment.q11_mentorship = form_data.get('q11_mentorship', [''])[0]
                assessment.q12_education_level = form_data.get('q12_education_level', [''])[0]
                assessment.q13_additional_education = form_data.get('q13_additional_education', [''])[0]
                assessment.q14_career_aspirations = form_data.get('q14_career_aspirations', [''])[0]
                assessment.q15_transition_timeline = form_data.get('q15_transition_timeline', [''])[0]
                
                assessment.status = 'completed'
                assessment.progress = 100
                assessment.completed_at = datetime.utcnow()
                
                db.session.commit()
                
                return redirect(url_for('assessment_processing', assessment_id=assessment_id))
            except Exception as e:
                flash(f'Error saving assessment: {str(e)}', 'error')
                return render_template('questions.html', assessment=assessment)
        
        return render_template('questions.html', assessment=assessment)
    
    @app.route('/assessment/<int:assessment_id>/save', methods=['POST'])
    @login_required
    def assessment_save_progress(assessment_id):
        """Auto-save assessment progress (AJAX endpoint)"""
        assessment = Assessment.query.get_or_404(assessment_id)
        
        if assessment.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        try:
            data = request.get_json()
            question = data.get('question')
            value = data.get('value')
            
            # Update specific question field
            if hasattr(assessment, question):
                setattr(assessment, question, value)
                assessment.last_updated = datetime.utcnow()
                db.session.commit()
                return jsonify({'success': True, 'message': 'Progress saved'})
            else:
                return jsonify({'success': False, 'message': 'Invalid question'}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/assessment/<int:assessment_id>/processing')
    @login_required
    def assessment_processing(assessment_id):
        """Process assessment with AI"""
        from database import Assessment
        from ai_service import analyze_career_assessment
        import json
        
        assessment = Assessment.query.get_or_404(assessment_id)
        
        if assessment.user_id != current_user.id:
            flash('Unauthorized access.', 'error')
            return redirect(url_for('dashboard'))
        
        # Check if already processed
        if assessment.status == 'completed' and assessment.results:
            return redirect(url_for('assessment_results', assessment_id=assessment_id))
        
        # Show loading page (AI processing happens in background)
        # In production, you'd use Celery/background tasks
        # For now, we'll process synchronously
        
        try:
            # Prepare data for AI
            assessment_data = {
                'q1_interests': assessment.q1_interests,
                'q2_environment': assessment.q2_environment,
                'q3_technical_skill': assessment.q3_technical_skill,
                'q3_communication_skill': assessment.q3_communication_skill,
                'q3_math_skill': assessment.q3_math_skill,
                'q3_creative_skill': assessment.q3_creative_skill,
                'q3_leadership_skill': assessment.q3_leadership_skill,
                'q3_detail_skill': assessment.q3_detail_skill,
                'q4_academic_subjects': assessment.q4_academic_subjects,
                'q5_underutilized_skills': assessment.q5_underutilized_skills,
                'q6_success_definition': assessment.q6_success_definition,
                'q7_motivation': assessment.q7_motivation,
                'q8_handle_setbacks': assessment.q8_handle_setbacks,
                'q10_work_life_balance': assessment.q10_work_life_balance,
                'q11_mentorship': assessment.q11_mentorship,
                'q12_education_level': assessment.q12_education_level,
                'q13_additional_education': assessment.q13_additional_education,
                'q14_career_aspirations': assessment.q14_career_aspirations,
                'q15_transition_timeline': assessment.q15_transition_timeline,
            }
            
            # Call AI service
            results = analyze_career_assessment(assessment_data)
            
            # Save results
            assessment.results = json.dumps(results)
            assessment.status = 'completed'
            assessment.completed_at = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            print(f"Error processing assessment: {e}")
            assessment.status = 'error'
            db.session.commit()
        
        return render_template('loading.html', assessment_id=assessment_id)

    @app.route('/assessment/<int:assessment_id>/results')
    @login_required
    def assessment_results(assessment_id):
        """Show results"""
        from database import Assessment
        import json
        
        assessment = Assessment.query.get_or_404(assessment_id)
        
        if assessment.user_id != current_user.id:
            flash('Unauthorized access.', 'error')
            return redirect(url_for('dashboard'))
        
        # Parse results from JSON string to Python dict
        results_data = None
        if assessment.results:
            try:
                if isinstance(assessment.results, str):
                    results_data = json.loads(assessment.results)
                else:
                    results_data = assessment.results
            except Exception as e:
                print(f"Error parsing results: {e}")
                results_data = None
        
        return render_template('results.html', assessment=assessment, results_data=results_data)

    return app



if __name__ == '__main__':
    env = os.getenv('FLASK_ENV', 'development')
    app = create_app(env)
    
    print("\n" + "="*60)
    print("🚀 Career Guidance AI - Phase 3")
    print("="*60)
    print(f"Environment: {env}")
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Server: http://localhost:5000")
    print("="*60 + "\n")
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=5000)
