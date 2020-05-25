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

import mlLib.trainModels as tm

trainingTypeChoices = [
            ('Kaggle', 'Kaggle'),
            ('Train-only',  'Train-only'),
            ('Predict', ' Predict'),
            ('Cluster', 'Cluster')
        ]


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

    modelType = SelectField(
        'modelType',
        validators=[DataRequired('A ML Model Type is required')],
        choices=[
            (tm.TRAIN_CLASSIFICATION, tm.TRAIN_CLASSIFICATION),
            (tm.TRAIN_REGRESSION, tm.TRAIN_REGRESSION),
            (tm.TRAIN_CLUSTERING, tm.TRAIN_CLUSTERING)
        ])

    trainingType = SelectField(
        'modelType',
        validators=[DataRequired('A training type is required')],
        choices=trainingTypeChoices)


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

    modelType = SelectField(
        'modelType',
        validators=[DataRequired('A ML Model Type is required')],
        choices=[
            (tm.TRAIN_CLASSIFICATION, tm.TRAIN_CLASSIFICATION),
            (tm.TRAIN_REGRESSION, tm.TRAIN_REGRESSION),
            (tm.TRAIN_CLUSTERING, tm.TRAIN_CLUSTERING)
        ])

    trainingType = SelectField(
        'modelType',
        validators=[DataRequired('A training type is required')],
        choices=trainingTypeChoices)


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

    clusterDimensionThreshold = IntegerField('clusterDimensionThreshold')

    scoring = SelectField(
        'scoring',
        validators=[DataRequired('A target scoring method is required')],
        choices=[])

    modelList = SelectMultipleField(
        'modelList',
        validators=[DataRequired('A ML Model is required')],
        choices=[])

    basicAutoMethod = BooleanField('basicAutoMethod', default=False)
