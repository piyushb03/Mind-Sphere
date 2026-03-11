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
