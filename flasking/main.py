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

import sqlite3
from registration import RegistrationForm
from flask import Flask, render_template, url_for, flash, redirect, g, request, session
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"




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
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None
        conn = sqlite3.connect("/var/www/flask/profiles.db")
        en = conn.cursor()
        user = en.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif user["password"] != password:
            error = "Incorrect password."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("login.html")


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='0.0.0.0')
