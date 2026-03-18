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
