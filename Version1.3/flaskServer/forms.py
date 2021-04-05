
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, 
    BooleanField, SubmitField,
    ValidationError)
from wtforms.validators import DataRequired, Email

from .extensions import mongo, mail, login

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('')

class RegistrationForm(FlaskForm):
    firstName = StringField('First name', validators=[DataRequired()])
    lastName = StringField('Last name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    institution = StringField('Institution', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = mongo.db.user.find_one({"email": email})
        if user is not None:
            return False
        return True

class ChangeEmailForm(FlaskForm):
    old = StringField('Old Email', validators=[DataRequired(), Email()])
    new = StringField('New Email', validators=[DataRequired(), Email()])
    submit = SubmitField('')

    def validate_email(self, old, new):
        oldEmail = mongo.db.user.find_one({"email": old})
        newEmail = mongo.db.user.find_one({"email": new})
        if oldEmail is not None and newEmail is None:
            return True
        return False

class ChangeInstitutionForm(FlaskForm):
    new = StringField('New Institution', validators=[DataRequired()])
    submit = SubmitField('')

#TODO add news, add glossary