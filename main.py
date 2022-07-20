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

from registration import RegistrationForm
from login import LoginForm

from flask import Flask, render_template, url_for, flash, redirect, session
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy

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

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password


@app.route("/")
def home():
    return render_template('home.html', subtitle='Home', text='this the home page')


@app.route("/calendar")
def calendar():
    return render_template('calendar.html')


@app.route("/habits")
def habits():
    return render_template('habits.html')


@app.route("/moods")
def moods():
    return render_template('moods.html')


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
        return redirect(url_for('home'))
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
            return render_template('profile.html')
        else:
            flash("incorrect username or password", 'failure')
    return render_template('login.html', form=form)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='0.0.0.0')
