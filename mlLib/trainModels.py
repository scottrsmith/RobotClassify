#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#    ML Lib Producivity Class Library
#    Copyright (C) 2019  Scott R Smith
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from __future__ import print_function
from __future__ import division

from sklearn.exceptions import DataConversionWarning, ConvergenceWarning
from sklearn.utils.testing import ignore_warnings

import pickle
import numpy as np
from time import time

import mlLib.mlUtility as mlUtility


# Import Elastic Net, Ridge Regression, and Lasso Regression
from sklearn.linear_model import ElasticNet, Ridge, Lasso, LinearRegression

# Import Random Forest and Gradient Boosted Trees
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import SCORERS
#  classification
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import BaggingClassifier, AdaBoostClassifier,\
    ExtraTreesClassifier, VotingClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC

from mlxtend.classifier import StackingClassifier

from xgboost import XGBClassifier

# Function for creating model pipelines
from sklearn.pipeline import make_pipeline

# For standardization
from sklearn.preprocessing import StandardScaler

# Helper for cross-validation
from sklearn.model_selection import GridSearchCV, ParameterGrid
from sklearn.exceptions import NotFittedError

# Import r2_score and mean_absolute_error functions
from sklearn.metrics import r2_score, mean_absolute_error, accuracy_score,\
    make_scorer, fbeta_score, confusion_matrix
from sklearn.metrics import f1_score, recall_score, precision_score

from sklearn.cluster import KMeans

# Classification metrics
from sklearn.metrics import roc_curve, auc, roc_auc_score

from sklearn.metrics import adjusted_rand_score

from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor

import tracemalloc


# pd.options.mode.chained_assignment = None  # default='warn'

TRAIN_CLASSIFICATION = 'Classification'
TRAIN_REGRESSION = 'Regression'
TRAIN_CLUSTERING = 'Clustering'

RUNDEFAULT = 'Run Default'
RUNLONG = 'Run Long'
RUNSHORT = 'Run Short'


availableModels = {TRAIN_REGRESSION: ['lasso', 'ridge', 'enet', 'rf', 'gb',
                                      'dtr', 'linearregression'],
                   # TRAIN_CLASSIFICATION: ['l1', 'l2', 'rfc', 'gbc',
                   #           'decisiontree', 'kneighbors', 'sgd', 'bagging',
                   TRAIN_CLASSIFICATION: ['l2', 'rfc', 'gbc', 'decisiontree',
                                          'kneighbors', 'sgd', 'bagging',
                                          'adaboost', 'gaussiannb', 'etc',
                                          'svc', 'xgbc', 'stack', 'vote'],
                   TRAIN_CLUSTERING: ['kmeans']}


def memorySnapshot(log, cnt=25, start=False):
    if start:
       tracemalloc.start()
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    print('\n\nTop {} at {}..............'.format(cnt, log))
    for stat in top_stats[:cnt]:
       print(stat)
    print ('\n')
    pass


def mapScoring(score):
    map = {'Precision': 'precision',
           'Recall': 'recall',
           'Accuracy': 'accuracy'}
    if score in map:
        return map[score]
    else:
        return score


def getModelPreferences(name, project, forBase=True, forMeta=False):
    if forMeta:
        if name in project.hyperparametersOverrideForMetaClassifier:
            override = project.hyperparametersOverrideForMetaClassifier[name]
        else:
            override = None

    elif forBase:
        if name in project.overrideHyperparameters:
            override = project.overrideHyperparameters[name]
        else:
            override = None
    else:  # hyperparametersOverrideForBaseEstimator
        if name in project.hyperparametersOverrideForBaseEstimator:
            override = project.hyperparametersOverrideForBaseEstimator[name]
        else:
            override = None

    # Regression models
    if project.modelType == TRAIN_REGRESSION:
        if name == 'lasso':
            return lassoPreferences(project, override, forBase, forMeta)
        elif name == 'ridge':
            return ridgePreferences(project, override, forBase, forMeta)
        elif name == 'enet':
            return enetPreferences(project, override, forBase, forMeta)
        elif name == 'rf':
            return rfPreferences(project, override, forBase, forMeta)
        elif name == 'gb':
            return gbPreferences(project, override, forBase, forMeta)
        elif name == 'dtr':
            return dtrPreferences(project, override, forBase, forMeta)
        elif name == 'linearregression':
            return linearRegressionPreferences(project, override, forBase)

    # Now classification models
    if project.modelType == TRAIN_CLASSIFICATION:
        if name == 'l1':
            return l1Preferences(project, override, forBase, forMeta)
        elif name == 'l2':
            return l2Preferences(project, override, forBase, forMeta)
        elif name == 'rfc':
            return rfcPreferences(project, override, forBase, forMeta)
        elif name == 'gbc':
            return gbcPreferences(project, override, forBase, forMeta)
        elif name == 'decisiontree':
            return dtcPreferences(project, override, forBase, forMeta)
        elif name == 'kneighbors':
            return kneighborsPreferences(project, override, forBase, forMeta)
        elif name == 'sgd':
            return sgdPreferences(project, override, forBase, forMeta)
        elif name == 'bagging':
            return baggingPreferences(project, override, forBase, forMeta)
        elif name == 'adaboost':
            return adaboostPreferences(project, override, forBase, forMeta)
        elif name == 'gaussiannb':
            return gaussiannbPreferences(project, override, forBase, forMeta)
        elif name == 'xgbc':
            return xgbcPreferences(project, override, forBase, forMeta)
        elif name == 'etc':
            return etcPreferences(project, override, forBase, forMeta)
        elif name == 'vote':
            return votePreferences(project, override, forBase, forMeta)
        elif name == 'stack':
            return stackPreferences(project, override, forBase, forMeta)
        elif name == 'svc':
            return svcPreferences(project, override, forBase, forMeta)

    # and now clustering
    if project.modelType == TRAIN_CLUSTERING:
        if name == 'kmeans':
            return kmeansPreferences(project, override, forBase, forMeta)

    return None


def getEstimatorPreferences(name, project, forMeta=False):
    names = name.split('+')
    if len(names) == 1:
        return getModelPreferences(names[0], project,
                                   forBase=True, forMeta=forMeta)
    else:
        baseName = names[0]
        estimatorName = names[1]
        # print ('estimatorName==',estimatorName)
        estimatorModel, paramsList, _ = getModelPreferences(estimatorName,
                                                            project,
                                                            forBase=False,
                                                            forMeta=forMeta)

        estimatorParamsFixed = fixHyperparameters(paramsList,
                                                  prefix='base_estimator__')
        model, hyperparams, modelScoringList = getModelPreferences(
            baseName,
            project,
            forBase=True,
            forMeta=forMeta)
        model.set_params(base_estimator=estimatorModel)
        hyperparams = fixHyperparameters(hyperparams)
        return model, merge2dicts(hyperparams,
                                  estimatorParamsFixed),
        modelScoringList


# ***************************
# regression
# ***************************


# Lasso regressor
def lassoPreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # Lasso hyperparameters

    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:  # Shorter run
        hyperparameters = {
            'lasso__alpha': [0.001, 0.01, 0.1, 1, 5, 10]
        }
    else:  # Longer run
        hyperparameters = {
            'lasso__alpha': [0.0001, 0.001, 0.005, 0.01, 0.05,
                             0.1, 0.5, 1, 5, 10, 50]
        }
    scorers = ['best', 'r2', 'MAE', 'score']
    return Lasso(random_state=project.randomState), hyperparameters, scorers


# Ridge Regressor
def ridgePreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # Ridge hyperparameters

    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:  # Shorter run
        hyperparameters = {
            'ridge__alpha': [0.001, 0.01, 0.1, 1, 5, 10]
        }
    else:  # Longer run
        hyperparameters = {
            'ridge__alpha': [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5, 10]
        }

    scorers = ['best', 'r2', 'MAE', 'score']
    return Ridge(random_state=project.randomState), hyperparameters, scorers


# Elastic Net Regression
def enetPreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # Elastic Net hyperparameters
    # Ridge hyperparameters

    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:  # Shorter run
        hyperparameters = {
            'elasticnet__alpha': [0.001, 0.01, 0.1, 1, 5, 10],
            'elasticnet__l1_ratio': [0.1, 0.5, 0.9]
        }
    else:  # Longer run
        hyperparameters = {
            'elasticnet__alpha': [0.001, 0.005, 0.01, 0.05,
                                  0.1, 0.5, 1, 5, 10],
            'elasticnet__l1_ratio': [0.1, 0.3, 0.5, 0.7, 0.9]
        }

    scorers = ['best', 'r2', 'MAE', 'score']

    return ElasticNet(random_state=project.randomState), hyperparameters,\
        scorers


# Random forests regressor
def rfPreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # Random forest hyperparameters

    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:  # Shorter run
        hyperparameters = {'randomforestregressor__n_estimators': [100, 200],
                           'randomforestregressor__max_features': ['auto',
                                                                   'sqrt',
                                                                   0.33]}
    else:  # Longer run
        hyperparameters = {'randomforestregressor__n_estimators': [50, 100,
                                                                   200, 500],
                           'randomforestregressor__max_features': ['auto',
                                                                   'sqrt',
                                                                   0.33]}

    scorers = ['best', 'r2', 'MAE', 'score']

    return RandomForestRegressor(random_state=project.randomState),\
        hyperparameters, scorers

# hyperparameter grid for the boosted tree Regressor


def gbPreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # Boosted tree hyperparameters

    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:  # Shorter run
        hyperparameters = {'gradientboostingregressor__n_estimators':
                           [100, 200],
                           'gradientboostingregressor__learning_rate':
                           [0.001, 0.01, 0.1],
                           'gradientboostingregressor__max_depth':
                           [1, 5]}
    else:  # Longer run
        hyperparameters = {'gradientboostingregressor__n_estimators':
                           [50, 100, 200, 500],
                           'gradientboostingregressor__learning_rate':
                           [0.001, 0.05, 0.1, 0.5],
                           'gradientboostingregressor__max_depth':
                           [1, 5, 10, 50]}

    scorers = ['best', 'r2', 'MAE', 'score']
    return GradientBoostingRegressor(random_state=project.randomState),\
        hyperparameters, scorers

# hyperparameter grid for the boosted tree Regressor


def dtrPreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # Boosted tree hyperparameters

    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:
        hyperparameters = {'decisiontreeregressor__max_depth': [1, 8, 32]}
    else:  # Longer run
        hyperparameters = {
            'decisiontreeregressor__max_depth': [1, 8, 16, 32, 64, 200]}

    scorers = ['best', 'r2', 'MAE', 'score']
    return DecisionTreeRegressor(random_state=project.randomState),\
        hyperparameters, scorers

# hyperparameter grid for the boosted tree Regressor


def linearRegressionPreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # Boosted tree hyperparameters

    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:
        hyperparameters = {}
    else:
        hyperparameters = {}

    scorers = ['best', 'r2', 'MAE', 'score']

    return LinearRegression(), hyperparameters, scorers


# ***************************
# Classifiers
# ***************************
def l1Preferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # for  L1L1 -regularized logistic regression

    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:
        hyperparameters = {
            'logisticregression__solver': ['liblinear'],
            'logisticregression__max_iter': [10, 15, 25],
            'logisticregression__C': [.01, .1, 10, 50]
        }
    else:
        hyperparameters = {
            'logisticregression__solver': ['liblinear', 'saga'],
            'logisticregression__C': [.000001, .0001, .001, .01, .1, 10, 30,
                                      50, 100, 250, 500, 1000],
            'logisticregression__max_iter': [5, 10, 15, 25, 50, 100, 300, 500]
        }

    if project.modelType == TRAIN_REGRESSION:
        scorers = ['best', 'r2', 'MAE', 'accuracy', 'score']
    elif project.modelType == TRAIN_CLASSIFICATION:
        scorers = ['best', 'r2', 'MAE', 'accuracy', 'auroc', 'fbeta',
                   'score', 'confusionmatrix', 'f1', 'recall', 'precision']
    else:
        scorers = []

    return LogisticRegression(penalty='l1', random_state=project.randomState),\
        hyperparameters, scorers


def l2Preferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # for  L2L2 -regularized logistic regression

    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:
        hyperparameters = {
            'logisticregression__solver': ['lbfgs', 'liblinear', 'sag'],
            'logisticregression__max_iter': [20, 25, 30],
            'logisticregression__C': [.001, .01, .1, 1.0, 10.]
        }
    else:
        hyperparameters = {
            'logisticregression__solver': ['newton-cg', 'lbfgs', 'liblinear',
                                           'sag', 'saga'],
            'logisticregression__C': [.000001, .0001, .001, .01, .1, 10, 50,
                                      100, 250, 500, 1000],
            'logisticregression__max_iter': [5, 10, 15, 25, 50, 100, 300, 500]
        }

    if project.modelType == TRAIN_REGRESSION:
        scorers = ['best', 'r2', 'MAE', 'accuracy', 'score']
    elif project.modelType == TRAIN_CLASSIFICATION:
        scorers = ['best', 'r2', 'MAE', 'accuracy', 'auroc', 'fbeta',
                   'score', 'confusionmatrix', 'f1', 'recall', 'precision']
    else:
        scorers = []

    return LogisticRegression(penalty='l2', random_state=project.randomState),\
        hyperparameters, scorers


def rfcPreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # Random forest hyperparameters

    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:
        hyperparameters = {
            'randomforestclassifier__n_estimators': [200, 250],
            'randomforestclassifier__max_features': [1.0, .80, 0.33]
        }

    else:
        hyperparameters = {'randomforestclassifier__max_features':
                           ['auto', 'sqrt', 1, 3, 10, .8, .33],
                           'randomforestclassifier__min_samples_split':
                           [2, 3, 10],
                           'randomforestclassifier__min_samples_leaf':
                           [1, 3, 10],
                           'randomforestclassifier__bootstrap': [False],
                           'randomforestclassifier__n_estimators':
                           [10, 50, 100, 300],
                           'randomforestclassifier__criterion': ['gini']}

    scorers = ['best', 'r2', 'MAE', 'accuracy', 'auroc', 'fbeta',
               'score', 'confusionmatrix', 'f1', 'recall', 'precision']
    return RandomForestClassifier(random_state=project.randomState),\
        hyperparameters, scorers


# hyperparameter grid for the  gradient boosted tree Classifier
def gbcPreferences(project, override, forBase, forMeta):
    #  gradient boosted tree
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:

        hyperparameters = {
            'gradientboostingclassifier__n_estimators': [300, 500],
            'gradientboostingclassifier__min_samples_split': [500],
            'gradientboostingclassifier__loss': ['deviance'],
            'gradientboostingclassifier__min_samples_leaf': [25],
            'gradientboostingclassifier__max_features': ['sqrt'],
            'gradientboostingclassifier__max_depth': [6, 8],
            'gradientboostingclassifier__learning_rate': [1., .1, .01],
            'gradientboostingclassifier__subsample': [.8],
            'gradientboostingclassifier__validation_fraction': [0.1],
            'gradientboostingclassifier__n_iter_no_change': [10],
            'gradientboostingclassifier__tol': [0.001]
        }
    else:
        hyperparameters = {
            'gradientboostingclassifier__min_samples_split': [2, 10],
            'gradientboostingclassifier__min_samples_leaf': [1, 5],
            'gradientboostingclassifier__max_features': ['sqrt', .3, 1.],
            'gradientboostingclassifier__subsample': [1., .8],
            'gradientboostingclassifier__n_estimators': [100],
            'gradientboostingclassifier__max_depth': [6, 8, 10],
            'gradientboostingclassifier__loss': ['exponential'],
            'gradientboostingclassifier__learning_rate': [.1, .01, ],
            'gradientboostingclassifier__validation_fraction': [0.1],
            'gradientboostingclassifier__n_iter_no_change': [10, 20],
            'gradientboostingclassifier__tol': [.1]
        }

        hyperparameters2 = {
            'gradientboostingclassifier__min_samples_split': [2, 100, 500],
            'gradientboostingclassifier__min_samples_leaf': [1, 50, 100, 150],
            'gradientboostingclassifier__max_features': ['sqrt', .3, .1],
            'gradientboostingclassifier__subsample': [1., .8],
            'gradientboostingclassifier__n_estimators': [100, 200, 300],
            'gradientboostingclassifier__max_depth': [6, 8, 10, 12],
            'gradientboostingclassifier__loss': ['exponential', 'deviance'],
            'gradientboostingclassifier__learning_rate': [.2, .1, .01, .05],
            'gradientboostingclassifier__validation_fraction': [0.1],
            'gradientboostingclassifier__n_iter_no_change': [5, 10],
            'gradientboostingclassifier__tol': [.1, .01, 0.001]
        }

    scorers = ['best', 'r2', 'MAE', 'accuracy', 'auroc', 'fbeta',
               'score', 'confusionmatrix', 'f1', 'recall', 'precision']
    return GradientBoostingClassifier(random_state=project.randomState),\
        hyperparameters, scorers

# hyperparameter grid for the boosted tree


def dtcPreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # Boosted tree hyperparameters
    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:

        hyperparameters = {
            'decisiontreeclassifier__splitter': ['best'],
            'decisiontreeclassifier__min_samples_leaf': [100, 150],
            'decisiontreeclassifier__min_samples_split': [100, 150],
            'decisiontreeclassifier__criterion': ['entropy'],
            'decisiontreeclassifier__max_features': [1.0],
            'decisiontreeclassifier__max_depth': [10]
        }
    else:
        hyperparameters = {
            'decisiontreeclassifier__criterion': ['entropy'],
            'decisiontreeclassifier__splitter': ['best', 'random'],
            'decisiontreeclassifier__min_samples_split': [2, 5, 10, 50, 100],
            'decisiontreeclassifier__min_samples_leaf': [1, 5, 10, 50, 100],
            'decisiontreeclassifier__max_features': ['sqrt', 'auto', 'log2',
                                                     1., .9, .2, .5],
            'decisiontreeclassifier__max_depth': [None, 1, 10, 25, 50,
                                                  100, 250]
        }

    scorers = ['best', 'r2', 'MAE', 'accuracy', 'auroc', 'fbeta',
               'score', 'confusionmatrix', 'f1', 'recall', 'precision']
    return DecisionTreeClassifier(random_state=project.randomState),\
        hyperparameters, scorers


# hyperparameter grid
def kneighborsPreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # hyperparameters
    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:
        hyperparameters = {'kneighborsclassifier__n_neighbors': [2, 10],
                           'kneighborsclassifier__leaf_size': [10, 40],
                           }
    else:  # Longer run
        hyperparameters = {'kneighborsclassifier__n_neighbors': [2, 4, 5, 10],
                           'kneighborsclassifier__leaf_size': [10, 20, 30, 40],
                           'kneighborsclassifier__p': [1, 2]
                           }

    scorers = ['best', 'r2', 'MAE', 'accuracy', 'auroc', 'fbeta',
               'score', 'confusionmatrix', 'f1', 'recall', 'precision']
    return KNeighborsClassifier(), hyperparameters, scorers

# hyperparameter grid


def sgdPreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # hyperparameters
    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
        # Loss: 'hinge', 'log', 'modified_huber', 'squared_hinge', 'perceptron'
        # regression loss: 'squared_loss', 'huber', 'epsilon_insensitive',
        #   or 'squared_epsilon_insensitive'
    elif toRun == RUNSHORT:  # short run
        hyperparameters = {
            'sgdclassifier__loss': ['hinge'],
            # 'none', 'l2', 'l1', or 'elasticnet'
            'sgdclassifier__penalty': ['l2'],
            'sgdclassifier__max_iter': [1000],
            'sgdclassifier__tol': [1e-3]
        }

    else:  # long run
        hyperparameters = {
            'sgdclassifier__loss': ['hinge', 'squared_loss', 'perceptron'],
            # 'none', 'l2', 'l1', or 'elasticnet'
            'sgdclassifier__penalty': ['l2', 'elasticnet'],
            'sgdclassifier__max_iter': [10, 100, 1000],
            'sgdclassifier__tol': [1e-1, 1e-2, 1e-3]
        }

    scorers = ['best', 'r2', 'MAE', 'accuracy', 'fbeta',
               'score', 'confusionmatrix', 'f1', 'recall', 'precision']
    return SGDClassifier(random_state=project.randomState),\
        hyperparameters, scorers

# hyperparameter grid


def gaussiannbPreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # hyperparameters
    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:  # short run
        hyperparameters = {'gaussiannb__var_smoothing': [1.0, .01, .001]}
    else:  # long run
        hyperparameters = {'gaussiannb__var_smoothing': [
            2., 1., 1e-2, 1e-1, 1e-3, 1e-5, 1e-9]}

    scorers = ['best', 'r2', 'MAE', 'accuracy', 'auroc', 'fbeta',
               'score', 'confusionmatrix', 'f1', 'recall', 'precision']
    return GaussianNB(), hyperparameters, scorers


# class xgboost.XGBClassifier(max_depth=3, learning_rate=0.1, n_estimators=100,
# verbosity=1, silent=None, objective='binary:logistic',
# booster='gbtree', n_jobs=1, nthread=None, gamma=0, min_child_weight=1,
# max_delta_step=0, subsample=1, colsample_bytree=1,
# colsample_bylevel=1, colsample_bynode=1, reg_alpha=0, reg_lambda=1,
# scale_pos_weight=1, base_score=0.5, random_state=0,
# seed=None, missing=None, **kwargs)
#
# xgbclassifier__
#
# hyperparameter grid
def xgbcPreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # hyperparameters
    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:  # short run
        hyperparameters = {'xgbclassifier__max_depth': [3, 5],
                           'xgbclassifier__gamma': [0, 0.1],
                           'xgbclassifier__colsample_bytree': [1],
                           'xgbclassifier__min_child_weight': [1],
                           'xgbclassifier__n_estimators': [50, 500]}
    else:  # long run
        hyperparameters = {'xgbclassifier__max_depth': [3, 5, 10, 25],
                           'xgbclassifier__gamma': [0, 0.1, .5],
                           'xgbclassifier__colsample_bytree': [1],
                           'xgbclassifier__min_child_weight': [1],
                           'xgbclassifier__n_estimators': [50, 100, 500]}

    scorers = ['best', 'r2', 'MAE', 'accuracy', 'auroc', 'fbeta',
               'score', 'confusionmatrix', 'f1', 'recall', 'precision']

    return XGBClassifier(), hyperparameters, scorers


# hyperparameter grid
def etcPreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # hyperparameters
    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:  # short run
        hyperparameters = {'extratreesclassifier__max_depth': [None],
                           'extratreesclassifier__max_features': [1, 3, 10],
                           'extratreesclassifier__min_samples_split':
                           [2, 3, 10],
                           'extratreesclassifier__min_samples_leaf':
                           [1, 3, 10],
                           'extratreesclassifier__bootstrap': [False],
                           'extratreesclassifier__n_estimators': [100, 300],
                           'extratreesclassifier__criterion': ['gini']}
    else:  # long run
        hyperparameters = {'extratreesclassifier__max_depth': [None, 5],
                           'extratreesclassifier__max_features':
                           [0.30, 0.50, 1.0, 10],
                           'extratreesclassifier__min_samples_split': [2, 10],
                           'extratreesclassifier__min_samples_leaf': [1, 10],
                           'extratreesclassifier__bootstrap': [False],
                           'extratreesclassifier__n_estimators': [100],
                           'extratreesclassifier__criterion': ['gini']}

        hyperparameters2 = {'extratreesclassifier__max_depth': [None, 5, 10],
                            'extratreesclassifier__max_features':
                            [0.40, 0.80, 1.0, 1, 3, 10],
                            'extratreesclassifier__min_samples_split':
                            [2, 3, 10],
                            'extratreesclassifier__min_samples_leaf':
                            [1, 3, 10],
                            'extratreesclassifier__bootstrap': [False],
                            'extratreesclassifier__n_estimators': [100, 300],
                            'extratreesclassifier__criterion': ['gini']}

    scorers = ['best', 'r2', 'MAE', 'accuracy', 'auroc', 'fbeta',
               'score', 'confusionmatrix', 'f1', 'recall', 'precision']
    return ExtraTreesClassifier(), hyperparameters, scorers
    return None, hyperparameters, scorers

# hyperparameter grid


def votePreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # hyperparameters
    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:  # short run
        hyperparameters = {}
    else:  # long run
        hyperparameters = {'votingclassifier__voting': ['hard', 'soft']
                           }

    scorers = ['best', 'r2', 'MAE', 'accuracy', 'fbeta',
               'score', 'confusionmatrix', 'f1', 'recall', 'precision']
    return None, hyperparameters, scorers

# hyperparameter grid


def svcPreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # hyperparameters
    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {'svc__probability': [True]}
    elif toRun == RUNSHORT:  # short run
        hyperparameters = {'svc__kernel': ['rbf'],
                           'svc__gamma': [0.001, 0.01, 0.1, 1],
                           'svc__C': [1, 10, 50, 100, 200, 300, 1000],
                           'svc__probability': [True]
                           }

    else:  # long run
        hyperparameters = {'svc__kernel': ['rbf'],
                           'svc__gamma': [0.001, 0.01, 0.1, 1],
                           'svc__C': [.1, 1, 10, 50, 100, 200, 300, 1000],
                           'svc__probability': [True]
                           }

    scorers = ['best', 'r2', 'MAE', 'accuracy', 'auroc', 'fbeta',
               'score', 'confusionmatrix', 'f1', 'recall', 'precision']
    return SVC(), hyperparameters, scorers


# hyperparameter grid
def stackPreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # hyperparameters
    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:  # short run
        hyperparameters = {'stackingclassifier__use_probas': [True, False],
                           }
    else:  # long run
        hyperparameters = {'stackingclassifier__use_probas': [True, False],
                           'stackingclassifier__average_probas': [True, False],
                           'stackingclassifier__use_features_in_secondary':
                           [True, False],
                           'stackingclassifier__use_clones': [True, False]
                           }

    scorers = ['best', 'r2', 'MAE', 'accuracy', 'auroc', 'fbeta',
               'score', 'confusionmatrix', 'f1', 'recall', 'precision']
    return None, hyperparameters, scorers


# hyperparameter grid
def baggingPreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:
        hyperparameters = {
            'baggingclassifier__max_features': [.75, 1.],
            'baggingclassifier__max_samples': [.75, 1.],
            'baggingclassifier__n_estimators': [50, 100]}
    else:
        hyperparameters = {
            'baggingclassifier__n_estimators': [5, 10, 100],
            'baggingclassifier__max_samples': [.5, .75, .95, .99, 1.],
            'baggingclassifier__max_features': [.50, .75, .95, .99, 1.]}

    scorers = ['best', 'r2', 'MAE', 'accuracy', 'auroc', 'fbeta',
               'score', 'confusionmatrix', 'f1', 'recall', 'precision']
    return BaggingClassifier(random_state=project.randomState),\
        hyperparameters, scorers


# hyperparameter grid
def adaboostPreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # hyperparameters
    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:  # long run
        hyperparameters = {'adaboostclassifier__n_estimators': [10, 100],
                           'adaboostclassifier__learning_rate': [.9, 1.0],
                           'adaboostclassifier__algorithm': ['SAMME.R']}
    else:  # long rur
        hyperparameters = {
            'adaboostclassifier__n_estimators': [10, 50, 100, 500],
            'adaboostclassifier__learning_rate': [.001, .01, .1, .2, 0.5, 1.0],
            'adaboostclassifier__algorithm': ['SAMME', 'SAMME.R']}

    scorers = ['best', 'r2', 'MAE', 'accuracy', 'auroc', 'fbeta',
               'score', 'confusionmatrix', 'f1', 'recall', 'precision']
    return AdaBoostClassifier(random_state=project.randomState),\
        hyperparameters, scorers


# ***************************
# clustering
# ***************************


# hyperparameter grid for the boosted tree Regressor
def kmeansPreferences(project, override, forBase, forMeta):
    # Pick wht hyperparameters this run is for. Model or its base estimator
    if forMeta:
        toRun = project.runMetaClassifier
    elif forBase:
        toRun = project.runHyperparameters
    else:
        toRun = project.runEstimatorHyperparameters

    # Boosted tree hyperparameters
    if override is not None:
        hyperparameters = override
    elif toRun == RUNDEFAULT:
        hyperparameters = {}
    elif toRun == RUNSHORT:
        hyperparameters = {}
    else:  # short run
        hyperparameters = {}

    scorers = []
    return KMeans(n_clusters=project.kmeansClusters,
                  random_state=project.randomState),\
        hyperparameters, scorers


def merge2dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


def fixHyperparameters(params, prefix=None):
    cleanParam = {}
    for p in params:
        paramName = p.split('__', 1)[1]
        value = params[p]
        if prefix is None:
            cleanParam[paramName] = value
        else:
            cleanParam[prefix+paramName] = value

    return cleanParam


@ignore_warnings(category=ConvergenceWarning)
@ignore_warnings(category=DataConversionWarning)
class trainModels (object):

    def __init__(self, tableName, project):

        # Split X and y into train and test sets
        self.X_train, self.X_test, self.y_train, self.y_test = \
            project.preppedData[tableName].getTrainingSet()

        self.project = project
        self.pipelines = {}
        self.hyperparameters = {}
        self.scoringList = {}
        self.modelListAsRun = None
        self.theLastRun = None
        project.modelListAsRun = []

        for name in project.modelList:
            memorySnapshot('name in project.modelList...', cnt=10)
            mlUtility.runLog('Prepping Model: '+name)

            names = name.split('+')
            stack = name.split(':')
            # mlUtility. traceLog(('Trace: name', name)
            # mlUtility. traceLog(('Trace: names and stack', names, stack)
            if len(names) == 1 and len(stack) == 1 and\
                    (stack == 'vote' or stack == 'stack'):
                pass
                # This is a special case, voting/stack will be done with
                # the best estimators
                # Find the best 5 models and rebuild name

                # names = nameStack.split('+')
                # stack = nameStack.split(':')
                # Get the list of trained models and their

            elif len(names) == 1 and len(stack) == 1:
                # estimator = False
                # print ('Name',name)
                model, hyperparams, modelScoringList = getModelPreferences(
                    name, project, forBase=True)
                # if project.useStandardScaler:
                #   self.pipelines[name]=make_pipeline(StandardScaler(),model)
                # else:
                #   self.pipelines[name] = make_pipeline(model)
                self.pipelines[name] = model
                self.hyperparameters[name] = fixHyperparameters(hyperparams)
                self.scoringList[name] = modelScoringList
                project.modelListAsRun.append(name)

            # This is for voting
            elif len(stack) > 2:
                stackName = stack[0]
                params = {}
                if stackName == 'vote':
                    _, hyperparams, modelScoringList = getModelPreferences(
                        stackName, project, forBase=True)
                    estimators = []
                    for i in range(1, len(stack)):
                        # Test if there is an alias for voter
                        if stack[i] in self.project.alias:
                            alias = self.project.alias[stack[i]]
                        else:
                            alias = stack[i]
                        if alias in project.modelListAsRun:
                            estimators.append(alias)
                        else:
                            mlUtility.errorLog(
                                'Estimator {} for VoteClasifier not found'.
                                format(alias))

                    # We need to setup the pipeline to set during fit, since
                    # the voting models need to be fit already
                    self.pipelines[name] = estimators
                elif stackName == 'stack':
                    model, hyperparams, modelScoringList = getModelPreferences(
                        stackName, project)
                    self.pipelines[name] = model

                    metaClassifierName = stack[-1]
                    _, P, _ = getEstimatorPreferences(
                        metaClassifierName, project, forMeta=True)
                    for p in P:
                        params['meta-'+p] = P[p]

                self.hyperparameters[name] = merge2dicts(
                    fixHyperparameters(hyperparams), params)
                self.scoringList[name] = modelScoringList
                project.modelListAsRun.append(name)

            # This is for
            elif len(names) == 2:
                model, hyperparams, modelScoringList = getEstimatorPreferences(
                    name, project)
                self.pipelines[name] = model
                self.hyperparameters[name] = hyperparams
                self.scoringList[name] = modelScoringList
                project.modelListAsRun.append(name)

            else:
                pass
                # Something went wrong

        self.modelType = project.modelType
        self.modelList = project.modelList
        self.modelListAsRun = project.modelListAsRun
        self.fittedModels = {}
        self.modelScores = {}
        self.shortModelScoresColumns = []

        self.bestModelName = None
        self.bestModelScore = None
        self.bestModel = None
        self.crossValidationSplits = project.crossValidationSplits
        self.parallelJobs = project.parallelJobs
        self.tableName = tableName

    def makeStackModel(self, name):
        bestScores = {}
        # bestParams = {}
        for n in self.fittedModels:
            bestScores[n] = self.fittedModels[n].best_score_
            # bestParams[name] = self.fittedModels[n].best_params_

        best = []
        # print ('best scores=',bestScores)
        for n, s in sorted(bestScores.items(),
                           key=lambda item: item[1],
                           reverse=True):
            if (n != 'vote'):
                best.append(n)
        #
        best = best[:min(4, len(best))]
        if name == 'stack':
            best.append('gaussiannb')

        mlUtility.runLog(
            '\n\0nRuning best models for stack {}:{}'.format(name, best))
        return (best)

    @ignore_warnings(category=ConvergenceWarning)
    @ignore_warnings(category=DataConversionWarning)
    def fitModels(self):

        # Create empty dictionary called fitted_models
        self.fittedModels = {}
        self.runTimes = {}

        # Loop through model pipelines, tuning each one and saving
        # it to fitted_models
        # for name, pipeline in self.pipelines.items():
        for name in self.pipelines:
            # Create cross-validation object from pipeline and hyperparameters
            memorySnapshot('Start...'+name, cnt=25)
            stackNameTest = name.split(':')
            if stackNameTest[0] == 'vote':
                estimators = []
                # mlUtility. traceLog(('pipelin=',self.pipelines[name])
                # print ('stackNameTest=',stackNameTest)
                if len(stackNameTest) == 1:
                    print('Makeing Voting')
                    self.pipelines[name] = self.makeStackModel(name)

                # This is really the list of etimators
                for voteName in self.pipelines[name]:
                    estimators.append(
                        tuple((voteName,
                               self.fittedModels[voteName].best_estimator_)))

                # mlUtility. traceLog(('Estimators=',estimators)
                pipelineRun = VotingClassifier(estimators=estimators)
            elif stackNameTest[0] == 'stack':
                # Get the meta classifier
                if len(stackNameTest) == 1:
                    stackingList = self.makeStackModel(stackNameTest[0])
                else:
                    stackingList = stackNameTest[1:]
                metaClassifierName = stackingList[-1]
                classifiers = []

                # build the classifiers
                # for each classifier, find the best paramaters:
                for stackClassifier in stackingList[1:-1]:
                    # print ('stackClassifier=',stackClassifier)

                    if stackClassifier in self.fittedModels:
                        # Get the best hyperparamaters
                        search = self.fittedModels[stackClassifier]
                        # hyperparams=
                        #      search.cv_results_['params'][search.best_index_]
                        hyperparamaters = search.best_params_

                        cls, _, _ = getEstimatorPreferences(
                            stackClassifier, self.project)

                        if 'random_state' in cls.get_params().keys():
                            cls.set_params(
                                **hyperparamaters,
                                random_state=self.project.randomState)
                        else:
                            cls.set_params(**hyperparamaters)
                        classifiers.append(cls)
                    else:
                        mlUtility.errorLog(
                            'Model {} for StackingClasifier not found'.
                            format(stackClassifier))

                # Get the meta classifier and add to stacking params
                metaClassifier, _, _ = getModelPreferences(
                    metaClassifierName, self.project, forBase=True)
                # add 'meta-
                pipelineRun = StackingClassifier(
                    classifiers=classifiers, meta_classifier=metaClassifier)

            else:
                pipelineRun = self.pipelines[name]
                # print ('Pipeline Name=',name)
                # print ('model pipelineRun run=',pipelineRun)

            runTimeStart = time()
            # mlUtility. traceLog(('Pipeline Run = ',pipelineRun)
            mlUtility.runLog('\n\nFitting: '+name)
            self.theLastRun = name

            if self.modelType == TRAIN_CLUSTERING:
                model = pipelineRun
                mlUtility.reOpenLogs()
                model.fit(self.X_train)
            else:
                # if name=='xgbc':
                #    parallelJobs = 1
                # else:
                #    parallelJobs = self.parallelJobs
                mlUtility.runLog(
                    'hyperparamaters for name: {} \n      {}'.format(
                        name,
                        self.hyperparameters[name]))
                mlUtility.runLog(pipelineRun)
                mlUtility.reOpenLogs()
                # model = GridSearchCV(pipelineRun,
                #                   fixHyperparameters(self.hyperparameters[name]),
                model = GridSearchCV(pipelineRun, self.hyperparameters[name],
                                     cv=self.crossValidationSplits,
                                     n_jobs=self.parallelJobs,
                                     verbose=self.project.gridSearchVerbose,
                                     scoring=mapScoring(
                                         self.project.gridSearchScoring),
                                     refit=True)

                if self.project.useStandardScaler:
                    mlUtility.runLog('Using Standard Scaler')
                    model.fit(StandardScaler().fit_transform(
                        self.X_train), self.y_train)
                else:
                    # print ('form.scoring..{}.\n\n'.format(SCORERS.keys()))
                    model.fit(self.X_train, self.y_train)

            # Fit model on X_train, y_train
            #    mlUtility.runLog ()
            #    mlUtility.runLog (('--------------------->', name))
            #    mlUtility.runLog (pipeline.get_params())
            #   mlUtility.runLog (self.X_train.describe())

            # Store model in fitted_models[name]
            self.fittedModels[name] = model
            self.runTimes[name] = (time() - runTimeStart) / 60.

            self.scoreModels(name, model)

            if self.modelType != TRAIN_CLUSTERING:
                fmt = "\n\n{} has been fit. The 'best' score is {:.4f}" +\
                          " with a runtime of {:.3f} Minutes"
                mlUtility.runLog(fmt.format(name,
                                            model.best_score_,
                                            self.runTimes[name]))
                mlUtility.runLog(
                    '   Best Paramaters= {}'.format(model.best_params_))
                self.project.logTrainingResults(
                    self.tableName,
                    self.project.logTrainingResultsFilename,
                    name)

                # Print out the current accumulated scores
                if self.project.ongoingReporting:
                    self.project.displayAllScores(
                        self.project.ongoingReportingFilename, short=True)

        self.getBestModel(self.project)
        return

    @ignore_warnings(category=ConvergenceWarning)
    @ignore_warnings(category=DataConversionWarning)
    def scoreModels(self, name, model):

        confusionMatrix = None
        fpr, tpr, thresholds = None, None, None

        r2 = None
        MAE = None
        auroc = None
        rocauc_score = None
        best = None
        accuracy = None
        fbeta = None
        score = None

        predProba = None
        pred = None

        f1, recall, precision = None, None, None

        try:

            # Get each score based upon the scorelist initilized for the model
            if self.y_test is not None:
                if self.project.useStandardScaler:
                    mlUtility.runLog('Using Standard Scaler')
                    X_test = StandardScaler().fit_transform(self.X_test)
                else:
                    X_test = self.X_test
                for scorer in self.scoringList[name]:
                    if scorer == 'best':
                        best = model.best_score_

                    elif scorer == 'r2':
                        if pred is None:
                            pred = model.predict(X_test)
                        r2 = r2_score(self.y_test, pred)

                    elif scorer == 'MAE':
                        if pred is None:
                            pred = model.predict(X_test)
                        MAE = mean_absolute_error(self.y_test, pred)

                    elif scorer == 'f1':
                        if pred is None:
                            pred = model.predict(X_test)
                        f1 = f1_score(self.y_test, pred)

                    elif scorer == 'recall':
                        if pred is None:
                            pred = model.predict(X_test)
                        recall = recall_score(self.y_test, pred)

                    elif scorer == 'precision':
                        if pred is None:
                            pred = model.predict(X_test)
                        precision = precision_score(self.y_test, pred)

                    elif scorer == 'accuracy':
                        if pred is None:
                            pred = model.predict(X_test)
                        accuracy = accuracy_score(self.y_test, pred)

                    elif scorer == 'auroc':
                        if predProba is None:
                            predProba = model.predict_proba(X_test)
                        # Area Under Receiver operating characteristic (AUROC)
                        rows, cols = predProba.shape
                        if cols == 2:
                            aurocPred = [p[1] for p in predProba]
                        else:
                            aurocPred = predProba
                        fpr, tpr, thresholds = roc_curve(
                            self.y_test, aurocPred)
                        auroc = auc(fpr, tpr)
                        rocauc_score = roc_auc_score(self.y_test, aurocPred)

                    elif scorer == 'fbeta':
                        if pred is None:
                            pred = model.predict(X_test)
                        fbeta = fbeta_score(
                            self.y_test, pred, beta=self.project.fbeta)

                    elif scorer == 'score':
                        if pred is None:
                            pred = model.predict(X_test)
                        score = model.score(X_test, pred)

                    elif scorer == 'confusionmatrix':
                        if pred is None:
                            pred = model.predict(X_test)
                        confusionMatrix = confusion_matrix(self.y_test, pred)
                        # confusionMatrix = confusionMatrix.astype('float')/
                        #                   confusionMatrix.sum(axis=0)

            # Track feature importance
            bestModel = model.best_estimator_
            coef = None
            fi = None
            if hasattr(bestModel, 'feature_importances_'):
                fi = bestModel.feature_importances_
            if hasattr(bestModel, 'coef_'):
                coef = bestModel.coef_[0]

                # Record the scores
            self.modelScores[name] = {'r2': r2,
                                      'MAE': MAE,
                                      'Best': best,
                                      'AUROC': auroc,
                                      'Accuracy': accuracy,
                                      'rocauc_score': rocauc_score,
                                      'fbeta': fbeta,
                                      'roc_curve': (fpr, tpr, thresholds),
                                      'CM': confusionMatrix, 'Score': score,
                                      'f1': f1,
                                      'Recall': recall,
                                      'Precision': precision,
                                      'RunTime': self.runTimes[name],
                                      'COEF': coef,
                                      'FI': fi}

            self.shortModelScoresColumns = ['r2', 'MAE', 'Best', 'AUROC',
                                            'Accuracy', 'fbeta',
                                            'Score', 'f1', 'Recall',
                                            'Precision', 'RunTime']

        except NotFittedError as e:
            mlUtility.runLog(repr(e))

        return

        # Display best_score_ for each fitted model
        # for name, model in fittedModels.items():
        #   mlUtility.runLog ( name, model.best_score_ )

    def getBestModel(self, project):
        def bestMod(fitModel):
            if hasattr(fitModel, 'best_estimator_'):
                return fitModel.best_estimator_
            else:
                return fitModel
        if self.project.testSize == 0:
            theBest = self.theLastRun
        elif self.project.goalsToReach is not None:
            theBest = self.getBestBySetGoals()
        elif self.modelType == TRAIN_CLASSIFICATION:
            theBest = self.getBestModelClassification()
        elif self.modelType == TRAIN_REGRESSION:
            theBest = self.getBestModelRegression()
        elif self.modelType == TRAIN_CLUSTERING:
            theBest = self.getBestModelClustering()

        self.bestModel = bestMod(self.fittedModels[theBest])
        self.bestModelName = theBest
        self.bestModelScore = self.modelScores[theBest]

        project.bestModelName = self.bestModelName
        project.bestModelScore = self.bestModelScore
        project.bestModel = self.bestModel

        return

    """
    Which model had the highest  R2R2  on the test set?
    Random forest

    Which model had the lowest mean absolute error?
    Random forest

    Are these two models the same one?
    Yes

    Did it also have the best holdout  R2R2  score from cross-validation?
    Yes

    Does it satisfy our win condition?
    Yes, its mean absolute error is less than $70,000!
    """

    def getBestModelRegression(self):
        # highest  R2R2  on the test set
        # lowest mean absolute error
        # Best holdout R2 (best score)
        if self.project.testSize == 0:
            return self.theLastRun

        highestR2 = None
        lowestMAE = None
        bestHoldoutR2 = None
        highestR2Name = None
        lowestMAEName = None
        bestHoldoutR2Name = None

        for name in self.modelScores:
            scores = self.modelScores[name]
            r2 = scores['r2']
            MAE = scores['MAE']
            Best = scores['Best']
            if highestR2 is None:
                highestR2 = r2
                lowestMAE = MAE
                bestHoldoutR2 = Best
                highestR2Name = name
                lowestMAEName = name
                bestHoldoutR2Name = name
            else:
                if r2 > highestR2:
                    highestR2 = r2
                    highestR2Name = name
                if MAE < lowestMAE:
                    lowestMAE = MAE
                    lowestMAEName = name
                if Best > bestHoldoutR2:
                    bestHoldoutR2 = Best
                    bestHoldoutR2Name = name

        if ((highestR2Name == lowestMAEName) and
                (lowestMAEName == bestHoldoutR2Name)):
            theBest = highestR2Name
        elif (highestR2Name == lowestMAEName):
            theBest = highestR2Name
        elif (lowestMAEName == bestHoldoutR2Name):
            theBest = lowestMAEName
        elif (highestR2Name == bestHoldoutR2Name):
            theBest = highestR2Name
        elif bestHoldoutR2Name is not None:
            theBest = bestHoldoutR2Name
        else:
            theBest = self.theLastRun

        return theBest

    def getBestModelClassification(self):
        # highest  R2R2  on the test set
        # lowest mean absolute error
        # Best holdout R2 (best score)
        if self.project.testSize == 0:
            return self.theLastRun

        highestAUROC = -np.inf
        bestAcc = -np.inf
        theBest = self.theLastRun

        for name in self.modelScores:
            scores = self.modelScores[name]
            auroc = scores['AUROC']
            acc = scores['Accuracy']
            if auroc is not None:
                if auroc > highestAUROC:
                    highestAUROC = auroc
                    theBest = name
        return theBest

    def getBestModelClustering(self):
        if self.project.testSize == 0:
            return self.theLastRun

        for name in self.modelScores:
            return name

    def getBestBySetGoals(self):
        if self.project.testSize == 0:
            return self.theLastRun
        theBest = {}
        theBestScore = {}
        bestNameCount = 0
        first = None

        # Set the vales at the worst
        for goal in self.project.goalsToReach:
            theBestScore[goal] = -np.inf
            theBest[goal] = None
            if first is None:
                first = goal

        # for each model, check each goal score,
        for name in self.modelScores:
            scores = self.modelScores[name]
            for goal in self.project.goalsToReach:
                if scores[goal] is not None:
                    if scores[goal] > theBestScore[goal]:
                        theBestScore[goal] = scores[goal]
                        theBest[goal] = name

        return theBest[first]
