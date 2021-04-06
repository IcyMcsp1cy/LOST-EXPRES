from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField,
    SubmitField,
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
        user = mongo.db.user.find_one({"email": email.data})
        if user is not None:
            return False
        return True


class ChangeEmailForm(FlaskForm):
    old = StringField('Old Email', validators=[DataRequired(), Email()])
    new = StringField('New Email', validators=[DataRequired(), Email()])
    submit = SubmitField('')

    def validate_old(self, old):
        if current_user.email != old.data:
            return False
        oldEmail = mongo.db.user.find_one({"email": old.data})
        return oldEmail is not None


    def validate_new(self, new):
        newEmail = mongo.db.user.find_one({"email": new.data})
        return newEmail is None


class ChangeInstitutionForm(FlaskForm):
    new = StringField('New Institution', validators=[DataRequired()])
    submit = SubmitField('')


class ForgotForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('')


#TODO add news, add glossary
