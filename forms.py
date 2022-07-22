from http.client import EXPECTATION_FAILED
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.widgets import ListWidget, CheckboxInput


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class JournalForm(FlaskForm):
    entry = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddHabitForm(FlaskForm):
    description = StringField('Habit', validators=[DataRequired(), Length(min=2, max=50)])
    importance = SelectField('Importance', choices=[
        (0, 'None'), (1, '!'), (2, '!!'), (3, '!!!')
    ],
    coerce=int)
    days = SelectMultipleField('Days',
                               validators=[],
                               widget=ListWidget(prefix_label=False),
                               option_widget=CheckboxInput(),
                               choices=[
                                ('sun', 'Sunday'),
                                ('mon', 'Monday'),
                                ('tues', 'Tuesday'),
                                ('wed', 'Wednesday'),
                                ('thurs', 'Thursday'),
                                ('fri', 'Friday'),
                                ('sat', 'Saturday')
                               ])
    submit = SubmitField('Add Habit')

class MoodForm(FlaskForm):
    happy = SubmitField("Happy")
    excited = SubmitField("Excited")
    sad = SubmitField("Sad")
    angry = SubmitField("Angry")
    scared = SubmitField("Scared")

class HabitForm(FlaskForm):
    submit = SubmitField('Submit')
