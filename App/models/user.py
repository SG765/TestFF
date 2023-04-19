from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from App.database import db
from datetime import datetime, date

#User model for user info
class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(120), nullable=False, unique=True)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(120), nullable=False)
  weight = db.Column(db.Float)
  height = db.Column(db.Float)
  age = db.Column(db.Integer)
  bio = db.Column(db.String(300))
  profile_image = db.Column(db.String(256), default='default-prof.jpeg')
  exercise = db.relationship('UserExercise', backref='user')
  progress = db.relationship('UserProgress', backref='user', uselist=False)

  def __init__(self, username, email, password):
    self.username = username
    self.email = email
    self.set_password(password)
    self.height = None
    self.weight = None
    self.age = None
    self.bio = None
    self.progress = UserProgress(user_id=self.id)

	#creates and adds a new exercise to the user's exercises
  def add_exercise(self, exercise_id, name, sets, reps, weight, time):
    exer = Exercise.query.get(exercise_id)
    if exer:
      try:
        exercise = UserExercise(self.id, exercise_id, name, sets, reps, weight, time)
        db.session.add(exercise)
        db.session.commit()
        return exercise
      except Exception:
        db.session.rollback()
        return None
    return None

  def get_json(self):
	  return {'id': self.id, 'username': self.username, 'email': self.email}

  def set_password(self, password):
	  """Create hashed password."""
	  self.password = generate_password_hash(password, method='sha256')

  def check_password(self, password):
	  """Check hashed password."""
	  return check_password_hash(self.password, password)

#To String method

  def __repr__(self):
	  return f'<User {self.id}: {self.username}>'

#Exercises for each user
class UserExercise(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  date = db.Column(db.Date, default=datetime.today().date(), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'))
  exercise = db.relationship('Exercise')
  name = db.Column(db.String(50))
  set = db.Column(db.Integer, nullable=True)
  rep = db.Column(db.Integer, nullable=True)
  weight = db.Column(db.Integer, nullable=True)
  time = db.Column(db.Integer, nullable=True)

  def __init__(self, user_id, exercise_id, name, set, rep, weight, time, date=None):
    self.user_id = user_id
    self.exercise_id = exercise_id
    self.name = name
    self.set = set
    self.rep = rep
    self.weight = weight
    self.time = time
    if date is None:
      self.date = datetime.utcnow()
    else:
      self.date = date

  def __repr__(self):
      return f'<UserExercise {self.id} : {self.name} User {self.user.username}>'

  def get_json(self):
    return {
      'id': self.id,
      'date': self.date.isoformat(),
      'user_id': self.user_id,
      'exercise_id': self.exercise_id,
      'name': self.name,
      'set': self.set,
      'rep': self.rep,
      'weight': self.weight,
      'time': self.time
    }

#Exercises on the system
class Exercise(db.Model):
  __tablename__ = 'exercise'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255), nullable=False)
  
  def get_json(self):
   return {
     'exercise_id': self.id,
     'name': self.name,
   }

#User's progress
class UserProgress(db.Model):
    __tablename__= "progress"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    steps_taken = db.Column(db.Integer, default=0)
    steps_goal = db.Column(db.Integer, default=10000)
    calories_burnt = db.Column(db.Integer, default=0)
    calorie_goal = db.Column(db.Integer, default=2000)
    water_drank = db.Column(db.Integer, default=0)
    date = db.Column(db.Date, nullable=False, default=datetime.now().date())


    def __init__(self, user_id, steps_taken=0, steps_goal=10000, calories_burnt=0, calorie_goal=2000, water_drank=0):
        self.user_id = user_id
        self.steps_taken = steps_taken
        self.steps_goal = steps_goal
        self.calories_burnt = calories_burnt
        self.calorie_goal = calorie_goal
        self.water_drank = water_drank
        self.date = datetime.now().date()

    def __repr__(self):
        return f"<UserProgress {self.user_id} - {self.date}>"

    def get_json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'steps_taken': self.steps_taken,
            'steps_goal': self.steps_goal,
            'calories_burnt': self.calories_burnt,
            'calorie_goal': self.calorie_goal,
            'water_drank': self.water_drank,
            'date': self.date.isoformat()
        }

