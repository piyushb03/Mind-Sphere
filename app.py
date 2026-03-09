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

