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

from forms import AddHabitForm, RegistrationForm, LoginForm

from flask import Flask, render_template, url_for, flash, redirect, session, g
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy

import functools

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
    date = db.Column(db.Date)
    entry = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    mood = db.Column(db.String(20), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(50), unique=True, nullable=False)
    importance = db.Column(db.Integer)
    success_rate = db.Column(db.Numeric)
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

@app.route("/")
def landing():
    return render_template('index.html', g=g)

@login_required
@app.route("/home")
def home():
    #return render_template('home.html', subtitle='Home', text='this the home page')
    return render_template('home.html')

@login_required
@app.route("/calendar")
def calendar():
    return render_template('calendar.html')

@login_required
@app.route("/habits")
def habits():
    data = Habit.query.filter_by(user_id=g.user.id).all()
    return render_template('habits.html', data=data)

@login_required
@app.route("/moods")
def moods():
    return render_template('moods.html')

@login_required
@app.route("/journal")
def journal():
    return render_template('journal.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)

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
        if 'sun' in form.data.get('days'):
            sun = True
        if 'mon' in form.data.get('days'):
            mon = True
        if 'tues' in form.data.get('days'):
            tues = True
        if 'wed' in form.data.get('days'):
            wed = True
        if 'thurs' in form.data.get('days'):
            thurs = True
        if 'fri' in form.data.get('days'):
            fri = True
        if 'sat' in form.data.get('days'):
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
