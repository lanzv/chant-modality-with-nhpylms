# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Author: Bas Cornelissen
# Copyright © 2020 Bas Cornelissen
# -----------------------------------------------------------------------------
"""
Traditional experiment
======================

The code is completely deterministic. We have verified that multiple runs give
identical results (see e.g. the md5 hashes of predictions that are logged,
of look at commit 88e5b9d1f49fae76bad4c68294669665a5a03a71 which does not 
include any changes to the predictions)
"""
import os
import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from src.load.features import initial, final, lowest, highest
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import accuracy_score, f1_score
from sklearn.metrics import classification_report
from src.load.representation import volpiano_to_midi

def get_classical_approach_score(train_segmentation, train_targets, 
                            test_semgnetation, test_targets,
                            n_iter=100, n_splits=5):
    """Runs a single experimental condition: trains the classifier, stores
    all the model, cross-validation results, and evaluation scores."""

    train_data = []
    for seg in train_segmentation:
        midi_sequence = volpiano_to_midi(''.join(seg))
        train_data.append([initial(midi_sequence), final(midi_sequence), highest(midi_sequence), lowest(midi_sequence)])
    test_data = []
    for seg in test_semgnetation:
        midi_sequence = volpiano_to_midi(''.join(seg))
        test_data.append([initial(midi_sequence), final(midi_sequence), highest(midi_sequence), lowest(midi_sequence)])

    # Model parameters and param grid for tuning
    fixed_params = {
        'random_state': np.random.randint(100),
        'n_jobs': -1,
        'min_samples_split': 2,
        'min_samples_leaf': 1,
        'max_leaf_nodes': None,
        'min_impurity_decrease': 0
    }
    param_grid = {
        'criterion': ['gini', 'entropy'],
        'n_estimators': np.arange(100, 1000),
        'max_depth': np.arange(1, 1000),
        'max_features': np.linspace(0, 1, 100),
        'bootstrap': [True, False],
        'max_samples': np.linspace(.5, 1, 100)
    }

    # Train and store the model
    model = RandomForestClassifier(**fixed_params)
    # Tune the model
    cv_results = tune_model(
        model=model, 
        data=train_data, 
        targets=train_targets, 
        param_grid=param_grid, 
        n_splits=n_splits, 
        n_iter=n_iter)
    
    # Train the model
    model.fit(train_data, train_targets)
    test_pred = model.predict(test_data)
    test_acc = accuracy_score(test_targets, test_pred)
    test_f1 = f1_score(test_targets, test_pred, average='weighted')
    
    return {"f1": test_f1, "accuracy": test_acc}




def tune_model(model, data, targets, param_grid, n_splits, n_iter):
    """"""
    rs = np.random.randint(100)
    # Tune!
    tuner = RandomizedSearchCV(
        estimator=model, 
        param_distributions=param_grid, 
        scoring=['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted'],
        cv=StratifiedKFold(n_splits=n_splits), 
        refit=False,
        n_iter=n_iter,
        n_jobs=-1,
        return_train_score=True,
        random_state=rs)
        
    tuner.fit(data, targets)
    cv_results = pd.DataFrame(tuner.cv_results_).sort_values('rank_test_accuracy')
    cv_results.index.name = 'id'
        
    # Log The best results
    best = cv_results.iloc[0, :]

    train_acc = best['mean_train_accuracy']
    test_acc = best['mean_test_accuracy']

    train_prec = best['mean_train_precision_weighted']
    test_prec = best['mean_test_precision_weighted']

    train_rec = best['mean_train_recall_weighted']
    test_rec = best['mean_test_recall_weighted']

    train_f1 = best['mean_train_f1_weighted']
    test_f1 = best['mean_test_f1_weighted']

    # Update model parameters
    model.set_params(**best.params)

    return cv_results