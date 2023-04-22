from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for, current_app, make_response, jsonify
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename 
import os
import random
from datetime import date, timedelta

from.index import index_views
from App.models import User, UserExercise, Exercise, UserProgress
from App.database import db

from App.controllers import (
    create_user,
    jwt_authenticate, 
    get_all_users,
    get_all_users_json,
    jwt_required,
    update_user,
		get_user_by_username,
    update_progress
)

user_views = Blueprint('user_views', __name__, template_folder='../templates')

@user_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)

@user_views.route('/api/users', methods=['GET'])
def get_users_action():
    users = get_all_users_json()
    return jsonify(users)

@user_views.route('/api/users', methods=['POST'])
def create_user_endpoint():
    data = request.json
    create_user(data['username'], data['email'], data['password'])
    return jsonify({'message': f"user {data['username']} created"})

@user_views.route('/users', methods=['POST'])
def create_user_action():
    data = request.form
    flash(f"User {data['username']} created!")
    create_user(data['username'], data['email'], data['password'])
    return redirect(url_for('user_views.get_user_page'))

@user_views.route('/static/users', methods=['GET'])
def static_user_page():
  return send_from_directory('static', 'static-user.html')

@user_views.route('/profile', methods=['GET'])
@login_required
def profile_page():
		user = User.query.filter_by(username=current_user.username).first()
		return render_template('profile.html', user=user)

@user_views.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    user = User.query.filter_by(username=current_user.username).first()
    if request.method == 'POST':
        # Get the form data
        bio = request.form['bio']
        weight = request.form['weight']
        height = request.form['height']
        age = request.form['age']
        image = request.files['image']

        # Handle the image file upload
        if image:
      # Delete the previous image if it's not the default one
          if user.profile_image != 'default-prof.jpeg':
            file_to_delete = os.path.join(current_app.root_path, 'static', 'user_images', user.profile_image)
            os.remove(file_to_delete)
			
			    # Save the new image
          filename = secure_filename(image.filename)
          file_path = os.path.join(current_app.root_path, 'static', 'user_images', filename)
          image.save(file_path)
        else:
          filename = None

        # Update the user object with the new values
        update_user(user.id, user.username, bio, weight, height, age, filename)

        # Redirect back to the profile page
        return redirect(url_for('user_views.profile_page', user=user))

    # If the request is GET, render the edit profile
    return render_template('edit-profile.html', user=user)

@user_views.route('/progress', methods=['GET'])
@login_required
def progress_page():
		progress = UserProgress.query.filter_by(user_id=current_user.id).first()
		today = date.today()
		oneweek = today - timedelta(days=6)
	
	#weekly progress
		progress_week = UserProgress.query.filter_by(user_id=current_user.id).filter(UserProgress.date >= oneweek).all()

	#dictionary for the days for the bar graph
		calories_dict = {'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0, 'Friday': 0, 'Saturday': 0, 'Sunday': 0}

		for days in progress_week:
			day = days.date.strftime('%A')
			calories_dict[day] += days.calories_burnt
			
		return render_template('progress.html', progress=progress, calories_dict=calories_dict)

#add exercise to UserExercise
@user_views.route('/exercise/<int:exercise_id>', methods=['POST'])
@login_required
def add_exercise(exercise_id):
  exercise = Exercise.query.get(exercise_id)
  exercise_name = exercise.name
  sets = request.form['sets']
  reps = request.form['reps']
  weight = request.form['weight']
  time = request.form['time']
  
  if(current_user.add_exercise(exercise_id, exercise_name, sets, reps, weight, time)==None):
    flash('Error')  
		
  user_exercises = UserExercise.query.all()
	
  flash('Set Logged')
  return redirect(url_for('user_views.workout_page'))


#retrieve from UserExercise
@user_views.route('/exercise', methods=['GET'])
@login_required
def user_exercise():
  user_exercises = UserExercise.query.all()
  if current_user.is_authenticated:
    return render_template(url_for('user_views.workout_page'), user_exercises=user_exercises)
  else:
    flash('Please log in to view this page', 'error')
    return redirect(url_for('auth.login'))

@user_views.route('/workout', methods=['GET'])
@user_views.route('/workout/<int:exercise_id>', methods=['GET'])
@login_required
def workout_page(exercise_id= 1):
  #get all
  exercises = Exercise.query.all()
  user_exercises = UserExercise.query.filter_by(user_id=current_user.id).all()
  sel_exercise = Exercise.query.get(exercise_id)
  print(exercises)
  return render_template('workout.html',
                         exercises=exercises,
                         user_exercises=user_exercises,
                         sel_exercise=sel_exercise)


#Remixer routes
@user_views.route('/remixer', methods=['GET'])
@user_views.route('/remixer/<int:exercise_id>', methods=['GET'])
@login_required
def random_exer(exercise_id=None):
  if(exercise_id==None):
    rando_num=random.randint(1,50)

  user_exercises = UserExercise.query.filter_by(user_id=current_user.id).all()
  sel_exercise = Exercise.query.get(rando_num)
  return render_template('remixer.html',
                         user_exercises=user_exercises,
                         sel_exercise=sel_exercise)

@user_views.route('/random', methods=['GET'])
@login_required
def user_remix():
  user_exercises = UserExercise.query.all()
  return render_template('remixer.html', user_exercises=user_exercises)

@user_views.route('/random/<int:exercise_id>', methods=['POST'])
@login_required
def add_remix(exercise_id):
    exercise = Exercise.query.get(exercise_id)
    exercise_name = exercise.name
    sets = request.form['sets']
    reps = request.form['reps']
    weight = request.form['weight']
    time = request.form['time']

    if not sets:
        sets = str(random.randint(1, 5))

    if not reps:
        reps = str(random.randint(1, 5))

    if not weight:
        weight = str(random.randint(1, 5))

    if not time:
        time = str(random.randint(1, 5))

    if current_user.add_exercise(exercise_id, exercise_name, sets, reps, weight, time) is None:
        flash('Error')

    flash('Set Logged')
    return redirect(url_for('user_views.random_exer'))

@user_views.route('/progress/add', methods=['POST'])
@login_required
def add_progress():
	user_id = current_user.id
	calories_burnt = request.form.get('calories_burnt')
	calorie_goal = request.form.get('calorie_goal')
	steps_taken = request.form.get('steps_taken')
	steps_goal = request.form.get('steps_goal')
	water_drank = request.form.get('water_drank')
	
	progress = UserProgress.query.filter_by(user_id=current_user.id).first()
	print(progress)
	if update_progress(user_id, calories_burnt, calorie_goal, steps_taken, steps_goal, water_drank):
		flash('Progress updated successfully', 'success')
	else:
		flash('Error')
	
	return redirect(url_for('user_views.progress_page'))

'''For the youtube tutorial route'''
@user_views.route('/youTutorial', methods=['GET'])
@user_views.route('/youTutorial/<int:exercise_id>', methods=['GET'])
@login_required
def get_Tut(exercise_id=1):
  exercises = Exercise.query.all()
  sel_exercise = Exercise.query.get(exercise_id)
  return render_template('youTutorial.html',
                         exercises=exercises,
                         sel_exercise=sel_exercise)