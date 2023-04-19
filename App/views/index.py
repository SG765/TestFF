from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, flash, url_for
from flask_login import login_required, login_user, current_user, logout_user
import traceback
from App.models import User
from App.database import db
from App.controllers import create_user

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
@index_views.route('/login', methods=['GET'])
def index_page():
    return render_template('index.html')

@index_views.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@index_views.route('/init', methods=['GET'])
def init():
    db.drop_all()
    db.create_all()
    create_user('bob', 'bob@bob.com', 'bobpass')
    return jsonify(message='db initialized!')

@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})
