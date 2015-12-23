# -*- coding: UTF-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, HiddenField
from wtforms.validators import DataRequired
# from flask import request


class LoginForm(Form):
    """Login form to access writing and settings pages"""
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    from_url = HiddenField('', validators=[DataRequired()])


class PersonForm(Form):
    """Staff form to edit a person data"""
    first_name = StringField('Имя', validators=[DataRequired()])
    middle_name = StringField('Отчество', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    graduated = StringField('Образование', validators=[DataRequired()])
    graduated_year = StringField('Год окончания', validators=[DataRequired()])
    date_of_birth = StringField('Дата рождения', validators=[DataRequired()])
    degree = StringField('Степень', validators=[DataRequired()])
    lab = StringField('Лаборатория', validators=[DataRequired()])
