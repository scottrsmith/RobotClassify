#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, \
    DateTimeField, BooleanField, IntegerField, FloatField
from wtforms import SubmitField
from wtforms.validators import DataRequired, AnyOf, URL, Optional, \
    NumberRange
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, DATA
import config


# ----------------------------------------------------------------------------
#  Project Form
# ----------------------------------------------------------------------------
class ProjectForm(FlaskForm):

    name = StringField(
        'name',
        validators=[DataRequired(message='Project Name Required')])

    description = StringField(
        'description',
        validators=[DataRequired(message='Description Required')])

    trainingFile = FileField(validators=[FileRequired(),
                                         FileAllowed(config.dataFiles,
                                                     'csv files only')])

    testingFile = FileField(validators=[FileRequired(),
                                        FileAllowed(config.dataFiles,
                                                    'csv files only')])


# ----------------------------------------------------------------------------
#  Project Form Edit
# ----------------------------------------------------------------------------
class ProjectFormEdit(FlaskForm):

    name = StringField(
        'name',
        validators=[DataRequired(message='Project Name Required')])

    description = StringField(
        'description',
        validators=[DataRequired(message='Description Required')])


# ----------------------------------------------------------------------------
#  Run Form
# ----------------------------------------------------------------------------
class RunForm(FlaskForm):

    name = StringField('name',
                       validators=[DataRequired(message='Run Name Required')])

    description = StringField(
        'description',
        validators=[DataRequired(message='Description Required')])

    targetVariable = SelectField(
        'targetVariable',
        validators=[DataRequired(
            message='Target Variable Required')],
        choices=[])

    key = SelectField(
        'key',
        validators=[DataRequired('The Primary key is required')],
        choices=[])

    predictSetOut = SelectMultipleField(
        'predictSetOut',
        validators=[DataRequired(
            'The Predict requires at least two choices')],
        choices=[])

    scoring = SelectField(
        'scoring',
        validators=[DataRequired('A target scoring method is required')],
        choices=[('f1', 'f1'),
                 ('r2', 'r2'),
                 ('Precision', 'Precision'),
                 ('Recall', 'Recall'),
                 ('Accuracy', 'Accuracy')])

    modelList = SelectMultipleField(
        'modelList',
        validators=[DataRequired('A ML Model is required')],
        choices=[
            ('l2', 'l2'),
            ('rfc', 'rfc'),
            # ('gbc', 'gbc'),
            ('decisiontree', 'decisiontree'),
            ('kneighbors', 'kneighbors'),
            # ('sgd', 'sgd'),
            ('bagging', 'bagging'),
            ('adaboost', 'adaboost'),
            ('gaussiannb', 'gaussiannb'),
            ('etc', 'etc'),
            # ('svc', 'svc'),
            ('xgbc', 'xgbc'),
            # ('stack', 'stack'),
            # ('vote', 'vote'),
        ])

    basicAutoMethod = BooleanField('basicAutoMethod', default=False)
