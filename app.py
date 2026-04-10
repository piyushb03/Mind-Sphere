from flask import Flask, render_template, url_for, flash, redirect, request, abort, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from datetime import datetime
from model_utils import engine
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
import os

# 1. Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# 2. Config - Use environment variables or fallbacks
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-fallback-123')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Google OAuth Keys (Loaded from .env)
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')

# 3. Initialize Extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# 4. OAuth Setup (The missing part that caused the error)
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)

# 5. Global Context for Templates
@app.context_processor
def inject_globals():
    return dict(formspree_endpoint=os.getenv('FORMSPREE_ENDPOINT'))

# --- Models (Unchanged) ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    assessments = db.relationship('Assessment', backref='author', lazy=True)

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    risk_score = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    
    age = db.Column(db.Integer)
    # Fields matching Survey.csv
    gender = db.Column(db.String(20))
    country = db.Column(db.String(50))
    occupation = db.Column(db.String(50))
    self_employed = db.Column(db.String(10))
    family_history = db.Column(db.String(10))
    days_indoors = db.Column(db.String(50))
    growing_stress = db.Column(db.String(50))
    changes_habits = db.Column(db.String(10))
    mental_health_history = db.Column(db.String(10))
    mood_swings = db.Column(db.String(20))
    coping_struggles = db.Column(db.String(10))
    work_interest = db.Column(db.String(20))
    social_weakness = db.Column(db.String(10))
    mental_health_interview = db.Column(db.String(10))
    care_options = db.Column(db.String(20))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/legal")
def legal():
    return render_template('legal.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        terms = request.form.get('terms')
        
        if not terms:
            flash('Please accept the Terms of Service.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('register'))
            
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.password != 'google-oauth' and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        elif user and user.password == 'google-oauth':
             flash('Please sign in with Google.', 'info')
        else:
            flash('Login unsuccessful. Check email and password.', 'danger')
    return render_template('login.html')

# --- Google OAuth Routes (The Fix) ---
@app.route('/login/google')
def google_login():
    return google.authorize_redirect(redirect_uri=url_for('google_callback', _external=True))

@app.route('/google/callback')
def google_callback():
    try:
        token = google.authorize_access_token()
        user_info = google.get('https://www.googleapis.com/oauth2/v2/userinfo').json()
        
        email = user_info['email']
        name = user_info['name']
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create user automatically if they don't exist
            user = User(username=name, email=email, password='google-oauth')
            db.session.add(user)
            db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Google Login Failed: {str(e)}', 'danger')
        return redirect(url_for('login'))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        try:
            # Capture Age separately
            age_input = request.form.get('age')

            # Gather inputs - Keys MUST match model_utils feature names
            input_data = {
                'Gender': request.form.get('gender'),
                'Country': request.form.get('country'),
                'Occupation': request.form.get('occupation'),
                'self_employed': request.form.get('self_employed'),
                'family_history': request.form.get('family_history'),
                'Days_Indoors': request.form.get('days_indoors'),
                'Growing_Stress': request.form.get('growing_stress'),
                'Changes_Habits': request.form.get('changes_habits'),
                'Mental_Health_History': request.form.get('mental_health_history'),
                'Mood_Swings': request.form.get('mood_swings'),
                'Coping_Struggles': request.form.get('coping_struggles'),
                'Work_Interest': request.form.get('work_interest'),
                'Social_Weakness': request.form.get('social_weakness'),
                'mental_health_interview': request.form.get('mental_health_interview'),
                'care_options': request.form.get('care_options')
            }
            
            # Predict
            result = engine.predict_risk(input_data)
            shap_plot = engine.generate_shap_plot(input_data)
            
            # Save to DB
            assessment = Assessment(
                risk_score=result['score'],
                risk_level=result['level'],
                author=current_user,
                age=age_input,
                gender=input_data['Gender'],
                country=input_data['Country'],
                occupation=input_data['Occupation'],
                self_employed=input_data['self_employed'],
                family_history=input_data['family_history'],
                days_indoors=input_data['Days_Indoors'],
                growing_stress=input_data['Growing_Stress'],
                changes_habits=input_data['Changes_Habits'],
                mental_health_history=input_data['Mental_Health_History'],
                mood_swings=input_data['Mood_Swings'],
                coping_struggles=input_data['Coping_Struggles'],
                work_interest=input_data['Work_Interest'],
                social_weakness=input_data['Social_Weakness'],
                mental_health_interview=input_data['mental_health_interview'],
                care_options=input_data['care_options']
            )
            db.session.add(assessment)
            db.session.commit()
            
            # Add Age to input_data for display
            input_data['Age'] = age_input

            return render_template('result.html', result=result, plot_url=shap_plot, input=input_data, timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            print(f"DEBUG ERROR: {e}")
            
    return render_template('dashboard.html')

@app.route("/history")
@login_required
def history():
    assessments = Assessment.query.filter_by(author=current_user).order_by(Assessment.date_posted.desc()).all()
    return render_template('history.html', assessments=assessments)

@app.route("/assessment/<int:assessment_id>")
@login_required
def view_previous_result(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    if assessment.author != current_user:
        abort(403)
        
    input_data = {
        'Age': assessment.age,
        'Gender': assessment.gender,
        'Country': assessment.country,
        'Occupation': assessment.occupation,
        'self_employed': assessment.self_employed,
        'family_history': assessment.family_history,
        'Days_Indoors': assessment.days_indoors,
        'Growing_Stress': assessment.growing_stress,
        'Changes_Habits': assessment.changes_habits,
        'Mental_Health_History': assessment.mental_health_history,
        'Mood_Swings': assessment.mood_swings,
        'Coping_Struggles': assessment.coping_struggles,
        'Work_Interest': assessment.work_interest,
        'Social_Weakness': assessment.social_weakness,
        'mental_health_interview': assessment.mental_health_interview,
        'care_options': assessment.care_options
    }
    
    result = engine.predict_risk(input_data)
    shap_plot = engine.generate_shap_plot(input_data)
    
    return render_template('result.html', result=result, plot_url=shap_plot, input=input_data, timestamp=assessment.date_posted.strftime("%Y-%m-%d %H:%M"))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)