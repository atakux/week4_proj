"""plan:

- we need a database
- we need to use flask for the user forms
        - login/registration
- pages to click on to add to journal, mood tracker, habit tracker
        - journal:
                - user is allowed to input whatever, similarly to notes.txt
                - maybe give a randomized daily prompt ?
        - mood tracker:
                - provide emojis/images for the user to click on ? or maybe a slider bar
                - allow selection of multiple emotions ?
        - habit tracker:
                - allow user to add/log new habits
                - allow user to track each time they do their habit
                - maybe display a graph or smth to show progress ?
                - allow user to delete habits
                - allow user to set long term goals besides regular habits ?
"""

from forms import AddHabitForm, JournalForm, RegistrationForm, LoginForm, MoodForm

from flask import Flask, render_template, url_for, flash, redirect, session, g, request
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy

import functools
from datetime import date


app = Flask(__name__)

proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = 'd821716fe32cfc57665bae47fc2d5dd3'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///profiles.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    journals = db.relationship('Journal', backref='user', lazy=True)
    moods = db.relationship('Mood', backref='user', lazy=True)
    habits = db.relationship('Habit', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
    def get_id(self):
        return self.id

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    entry = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Journal({self.date}, {self.entry[:20]})"

class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    mood = db.Column(db.String(20), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(50), unique=True, nullable=False)
    importance = db.Column(db.Integer)
    sunday = db.Column(db.Boolean)
    monday = db.Column(db.Boolean)
    tuesday = db.Column(db.Boolean)
    wednesday = db.Column(db.Boolean)
    thursday = db.Column(db.Boolean)
    friday = db.Column(db.Boolean)
    saturday = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Habit('{self.description}', '{self.importance}')"

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        
        return view(**kwargs)
    
    return wrapped_view

@app.route("/")
def landing():
    return render_template('index.html', g=g)


def get_todays_habits():
    today = date.today().weekday()
    habits = []
    if today == 0:
        habits = Habit.query.filter(Habit.monday == True).all()
    elif today == 1:
        habits = Habit.query.filter(Habit.tuesday == True).all()
    elif today == 2:
        habits = Habit.query.filter(Habit.wednesday == True).all()
    elif today == 3:
        habits = Habit.query.filter(Habit.thursday == True).all()
    elif today == 4:
        habits = Habit.query.filter(Habit.friday == True).all()
    elif today == 5:
        habits = Habit.query.filter(Habit.saturday == True).all()
    elif today == 6:
        habits = Habit.query.filter(Habit.sunday == True).all()
    return habits


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    habits = get_todays_habits()
    already_wrote_journal = Journal.query.filter_by(date=date.today()).first()
    if already_wrote_journal:
        journal_form = None
    else:
        journal_form = JournalForm()
    already_logged_mood = Mood.query.filter_by(date=date.today()).first()
    if already_logged_mood:
        mood_form = None
    else:
        mood_form = MoodForm()
    return render_template('home.html', habits=habits, journal_form=journal_form, mood_form=mood_form)

@app.route("/home/journal", methods=["POST"])
@login_required
def journal_submit():
    habits = get_todays_habits()
    journal_form = JournalForm()
    mood_form = MoodForm()
    if journal_form.validate_on_submit():
        journal = Journal(entry=journal_form.entry.data,
                          date=date.today(),
                          user_id=g.user.id)
        db.session.add(journal)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('home.html', habits=habits, journal_form=journal_form, mood_form=mood_form)
    

@app.route("/home/mood", methods=["POST"])
@login_required
def mood_submit():
    habits = get_todays_habits()
    journal_form = JournalForm()
    mood_form = MoodForm()
    if mood_form.validate_on_submit():
        mood = None
        if mood_form.happy.data:
            mood = 'Happy'
        elif mood_form.excited.data:
            mood = 'Excited'
        elif mood_form.sad.data:
            mood = 'Sad'
        elif mood_form.angry.data:
            mood = 'Angry'
        elif mood_form.scared.data:
            mood = 'Scared'
        mood_entry = Mood(date=date.today(),
                          mood=mood,
                          user_id = g.user.id)
        db.session.add(mood_entry)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('home.html', habits=habits, journal_form=journal_form, mood_form=mood_form)


@app.route("/calendar")
@login_required
def calendar():
    return render_template('calendar.html')

@app.route("/habits")
@login_required
def habits():
    habits = Habit.query.filter_by(user_id=g.user.id).all()
    return render_template('habits.html', habits=habits)


@app.route("/moods")
@login_required
def moods():
    moods = Mood.query.filter_by(user_id=g.user.id).all()
    return render_template('moods.html', moods=moods)


@app.route("/journal")
@login_required
def journal():
    journals = Journal.query.filter_by(user_id=g.user.id).all()
    return render_template('journal.html', journals=journals)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()

        flash(f'Digital Bullet Journal account created for {form.username.data}!!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Sign Up', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        actual_user = User.query.filter_by(username=form.username.data).first()

        if actual_user is None:
            flash("incorrect username or password", 'failure')
        elif actual_user.get_username() == form.username.data and \
                actual_user.get_password() == form.password.data:
            flash(f"welcome {actual_user.get_username()}!", 'success')
            session.clear()
            session['user_id'] = actual_user.get_id()
            return redirect(url_for('home'))
        else:
            flash("incorrect username or password", 'failure')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@login_required
@app.route("/habits/add", methods=["GET", "POST"])
def add_habit():
    form = AddHabitForm()
    if form.validate_on_submit():
        sun = mon = tues = wed = thurs = fri = sat = False
        if 'sun' in form.days.data:
            sun = True
        if 'mon' in form.days.data:
            mon = True
        if 'tues' in form.days.data:
            tues = True
        if 'wed' in form.days.data:
            wed = True
        if 'thurs' in form.days.data:
            thurs = True
        if 'fri' in form.days.data:
            fri = True
        if 'sat' in form.days.data:
            sat = True
        habit = Habit(description=form.data.get('description'),
                      importance=form.data.get('importance'),
                      sunday=sun,
                      monday=mon,
                      tuesday=tues,
                      wednesday=wed,
                      thursday=thurs,
                      friday=fri,
                      saturday=sat,
                      user_id=g.user.id)
        
        db.session.add(habit)
        db.session.commit()
        return redirect(url_for('habits'))
    return render_template("add_habit.html", form=form)


@app.before_request
def load_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()
  



if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='0.0.0.0')
