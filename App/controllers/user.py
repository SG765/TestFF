from flask import Blueprint, request, render_template, flash, redirect, url_for, current_app
from flask_login import login_user
from App.models import User, Exercise, UserExercise, UserProgress
from App.database import db
from werkzeug.utils import secure_filename
import os
 

def create_user(username, email, password):
    newuser = User(username=username, email=email, password=password)
    db.session.add(newuser)
    db.session.commit()
    return newuser

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def get_user(id):
    return User.query.get(id)

def get_all_users():
    return User.query.all()

def get_all_users_json():
    users = User.query.all()
    if not users:
        return []
    users = [user.get_json() for user in users]
    return users

def update_user(id, username, bio, weight, height, age, image):
    user = get_user(id)
    if user:
        user.username = username
        user.bio = bio
        if weight:
            user.weight = weight
        if height:
            user.height = height
        if age:
            user.age = age
        if image:
            user.profile_image = image
        db.session.add(user)
        db.session.commit()
        return True
    return False

def update_progress(id, calories_burnt, calorie_goal, steps_taken, steps_goal, water_drank):
    user = get_user(id)
    if user:
        if calories_burnt:
            user.progress.calories_burnt = calories_burnt
        if calorie_goal:
            user.progress.calorie_goal = calorie_goal
        if steps_taken:
            user.progress.steps_taken = steps_taken
        if steps_goal:
            user.progress.steps_goal = steps_goal
        if water_drank:
            user.progress.water_drank = water_drank
        db.session.commit()
        return True
    else:
        return False
