from flask import Blueprint, request, flash, redirect, url_for
from flask_login import login_user, login_manager, logout_user, LoginManager
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
import traceback

from App.models import User
from App.database import db

auth_viewsC = Blueprint("auth_viewsC", __name__)

def jwt_authenticate(username, password):
  user = User.query.filter_by(username=username).first()
  if user and user.check_password(password):
    return create_access_token(identity=username)
  return None

def login(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None

def setup_flask_login(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    return login_manager

def setup_jwt(app):
    jwt = JWTManager(app)

    @jwt.user_identity_loader
    def user_identity_lookup(identity):
        user = User.query.filter_by(username=identity).one_or_none()
        if user:
            return user.id
        return None

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.get(identity)

    return jwt

@auth_viewsC.route('/signup', methods=['GET', 'POST'])
def signup_action():
    if request.method == 'POST':
        data = request.form
        existing_username = User.query.filter_by(username=data['username']).first()
        existing_email = User.query.filter_by(email=data['email']).first()
        if existing_username:
            flash('Username already exists.')
            return redirect(url_for('index_views.signup_page'))
        if existing_email:
            flash('Email already exists.')
            return redirect(url_for('index_views.signup_page'))
        newUser = User(username=data['username'], email=data['email'], password=data['password'])
        try:
            db.session.add(newUser)
            db.session.commit()
            login_user(newUser)
            flash('Account Created!')
            return redirect(url_for('user_views.profile_page'))
        except Exception:
            db.session.rollback()
            return redirect(url_for('index_views.signup_page'))
    else:
        return redirect(url_for('index_views.signup_page'))