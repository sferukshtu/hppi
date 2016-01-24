# -*- coding: UTF-8 -*-
from app import app
from flask.ext.wtf import Form
from flask.ext.admin.form.upload import FileUploadField
from wtforms import StringField, PasswordField, HiddenField, DateField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os.path as op
from collections import defaultdict


def prefix_name(obj, file_data):
    parts = op.splitext(file_data.filename)
    return secure_filename('file-%s%s' % parts)


class LoginForm(Form):
    """Login form to access writing and settings pages"""
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    from_url = HiddenField('', validators=[DataRequired()])


class PersonForm(Form):
    """Staff form to edit a person data"""
    first_name = StringField('Имя', validators=[DataRequired()])
    middle_name = StringField('Отчество')
    surname = StringField('Фамилия', validators=[DataRequired()])
    # email = StringField('Email', validators=[DataRequired()])
    graduated = StringField('Образование')
    graduated_year = StringField('Год окончания')
    date_of_birth = DateField('День рождения', format='%d-%m-%Y')
    degree = StringField('Степень')
    lab = StringField('Лаборатория')
    prnd = StringField('ПРНД')
    publist = FileUploadField('File', namegen=prefix_name)
    # from_url = HiddenField('', validators=[DataRequired()])


class CalcForm(Form):
    """Calc form to calculate ratings"""
    val = app.config['SETTINGS'].find_one({"set_id": "prnd"})
    formula = val["prnd"]  # if val["prnd"] else formula = "pub_num+o_num+doc_num+exp_num+j_num+res_num+ms_num+phd_num+st_num+conf_num+pop_num+infl_num+ser_num"
    prnd = StringField('Формула', default=formula)
    defs = FileUploadField('File', namegen=prefix_name)


class RatingForm(Form):
    """Rating form to calc PRND"""
    val = app.config['RATING'].find({}, {"code": 1})
    # prs = app.config['STAFF'].find_one({"email": email})
    # arr = prs["prnd_data"][0]
    # print email
    for entry in val:
        # c = StringField(default=arr[str(entry["code"])])
        c = StringField()
        exec(entry["code"] + " = c")


class key_values_string():

    def __init__(self, dd):
        self.dd = dd

    def packed(self):
        val_dict = self.dd
        # vls = ", ".join(['{}={}'.format(k, v) for k, v in val_dict.iteritems()])
        for k, v in val_dict.iteritems():
            exec(k + " = v")
