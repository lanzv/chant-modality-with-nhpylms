import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import loguniform
import numpy as np
import logging
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from pandas import DataFrame
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import MultinomialNB
import random

"""
Model described in ISMIR2020 by Bas Cornelissen.
SVCLinear model to predict modes based on chant segmentation.
"""
class _SVMClassifierModel:
    def run(self, X_train, y_train, X_test, y_test,
            n_iter=100, n_splits=5, all_features_vectorizer=False):
        """
        Run method that initialize model and train it by calling
        other functions. Inspired by Bacor.

        Parameters
        ----------
        X_train : list of strings
            list of train chants represented as a string with segments separated by spaces
        y_train : list of strings
            list of train modes
        X_test : list of strings
            list of train chants represented as a string with segments separated by spaces
        y_test : list of strings
            list of test modes
        n_iter : int
            number of SVC iterations
        n_splits : int
            splists for cross validation for Stratified K Fold     
        all_features_vectorizer : boolean
            true to not limit number of features considered by vectorizer
            false when using 5000 as max features
        Returns
        -------
        train_pred : list of strings
            mode predictions of the model of training dataset
        test_pred : list of strings
            mode prediction of the model of testing dataset
        """
        train_data, train_targets = X_train, y_train
        test_data, test_targets = X_test, y_test

        # Linear SVC
        tuned_params = {
            'clf__C': loguniform(1e-3, 1e4),
            'clf__dual': [True, False]
        }
        self.model = get_svm_model(all_features_vectorizer)

        # Train the model
        return self.__train_model(
            train_data=train_data,
            train_targets=train_targets,
            test_data=test_data,
            param_grid=tuned_params,
            n_splits=n_splits,
            n_iter=n_iter
        )

    def evaluate(self, train_pred, train_gold, test_pred, test_gold):
        """
        Evaluate accuracy, f1, precision and recall of predictions and gold modes
        for both, train and test datasets.

        Parameters
        ----------
        train_pred : list of strings
            list of predicted modes of training chants
        train_gold : list of strings
            list of gold modes of training chants
        test_pred : list of strings
            list of predicted modes of testing chants
        test_gold : list of strings
            list of predicted modes of testing chants
        Returns
        -------
        scores : dict
            dictionary of scores, there are two keys: train, test
            each value is also dictionary of accuracy, f1, precision and recall scores
        """
        scores = {"train": {}, "test": {}}
        scores["train"] = dict(
            accuracy = accuracy_score(train_gold, train_pred),
            f1 = f1_score(train_gold, train_pred, average='weighted'),
            precision = precision_score(train_gold, train_pred, average='weighted'),
            recall = recall_score(train_gold, train_pred, average='weighted'),
        )
        scores["test"] = dict(
            accuracy = accuracy_score(test_gold, test_pred),
            f1 = f1_score(test_gold, test_pred, average='weighted'),
            precision = precision_score(test_gold, test_pred, average='weighted'),
            recall = recall_score(test_gold, test_pred, average='weighted'),
        )
        return scores


    # ------------------------- Training methods -------------------------


    def __train_model(self,
        train_data, train_targets, test_data,
        param_grid, n_splits, n_iter):
        """
        Do the training of the Bacor's SVC model. Before fitting model.. tune the model  (for finding the best
        clf__C and clf_dual values). Create predictions of training and testing datasets and
        return them back.


        Parameters
        ----------
        train_data : list of strings
            list of train chants represented as string of segments separated by spaces
        train_targets: list of strings
            list of train modes
        test_data : list of strings
            list of test chants represented as string of segments separated by spaces
        param_grid : dict
            dictionary of parameters to tune
        n_iter : int
            number of SVC iterations
        n_splits : int
            splists for cross validation for Stratified K Fold
        Returns
        -------
        train_pred : list of strings
            mode predictions of the model of training dataset
        test_pred : list of strings
            mode prediction of the model of testing dataset
        """
        # Tune the model
        self.__tune_model(
            data=train_data,
            targets=train_targets,
            param_grid=param_grid,
            n_splits=n_splits,
            n_iter=n_iter)
        # Train the model
        self.model.fit(train_data, train_targets)

        # Predictions
        train_pred = self.model.predict(train_data)
        test_pred = self.model.predict(test_data)
        return train_pred, test_pred


    def __tune_model(self, data, targets, param_grid, n_splits, n_iter):
        """
        Tune SVC model by param_grid values. 

        Parameters
        ----------
        data : list of strings
            list of training chants represented as string of segments seperated by spaces
        targets : list of strings
            list of gold training modes
        param_grid : dict
            dictionary of parameters to tune
        n_iter : int
            number of SVC iterations
        n_splits : int
            splists for cross validation for Stratified K Fold
        Returns
        -------
        cv_results : list or dict of floats
            cross validation results
        """
        rs = np.random.randint(100)

        # Tune!
        tuner = RandomizedSearchCV(
            estimator=self.model,
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

        # Update model parameters
        self.model.set_params(**best.params)

        return cv_results



def svm_classification_score(train_segmented_chants, train_modes,
               test_segmented_chants, test_modes, seed = 0):
    """
    Compute svm classification score scores - accuracy and f1 - of SVC Linear model to predict
    modes the most accurate based on the given chant segmentation.

    Parameters
    ----------
    train_segmented_chants : list of lists of strings
        list of segmented train chants represented as a list of string segments
    train_modes : list of strings
        list of train modes
    test_segmented_chants : list of lists of strings
        list of segmented train chants represented as a list of string segments
    test_modes : list of strings
        list of test modes
    seed : int
        random seed
    Returns
    -------
    scores : dict
        dictionary of scores, there are two keys: train, test
        each value is also dictionary of accuracy, f1, precision and recall scores
    """
    model = _SVMClassifierModel()
    # set seed
    np.random.seed(seed)

    # prepare data
    train_data = list2string(train_segmented_chants)
    test_data = list2string(test_segmented_chants)

    # train
    train_pred, test_pred = model.run(X_train = train_data, y_train = train_modes,
                                       X_test = test_data, y_test = test_modes)
    logging.info("The SVC model was trained with {} training data and {} testing data."
        .format(len(train_modes), len(test_modes)))

    # evaluate
    scores = model.evaluate(train_pred, train_modes, test_pred, test_modes)


    return {"f1": scores["test"]["f1"], "accuracy": scores["test"]["accuracy"]}








def list2string(segmented_chants):
    """
    Convert chant segments in list to chant segments in string for all chants.
    New chant representation is a string of segments separated by spaces.
    E.g. [["aaa", "bbb", "ccc"]] -> ["aaa bbb ccc"]

    Parameters
    ----------
    segmented_chants : list of lists of strings
        list of chants, each chant is represented as list of segments
    Returns
    -------
    string_segmentations : list of strings
        list of chants, each chant is represented as string, where segments are separated by spaces
    """
    string_segmentations = []
    for chant_segments in segmented_chants:
        string_segmentations.append(' '.join(chant_segments))
    return string_segmentations







def get_svm_model(all_features_vectorizer=False):
    """
    Get the Linear SVC model with their hyperparameters and TfidfVectorizer.
    Hyperparameters are not tuned. We use this model only for fast iteraion evaluation.
    For the final evlauation score is used the BACOR model version which is tuned.
    
    Parameters
    ----------
    all_features_vectorizer : boolean
        true to not limit number of features considered by vectorizer
        false when using 5000 as max features
    Returns
    -------
    pipeline : Pipeline
        sklearn pipeline of TfidfVectorizer and LinearSVC, basically pipeline of BACOR model
    """
    if all_features_vectorizer:
        tfidf_params = dict(
            # Defaults
            strip_accents=None,
            stop_words=None,
            ngram_range=(1,1),
            max_df=1.0,
            min_df=1,
            use_idf=True,
            smooth_idf=True,
            sublinear_tf=False,
            lowercase=False,
            analyzer='word',
            token_pattern=r'[^ ]+')
    else:
        tfidf_params = dict(
            # Defaults
            strip_accents=None,
            stop_words=None,
            ngram_range=(1,1),
            max_df=1.0,
            min_df=1,
            max_features=5000,
            use_idf=True,
            smooth_idf=True,
            sublinear_tf=False,
            lowercase=False,
            analyzer='word',
            token_pattern=r'[^ ]+')
    svc_params = {
        'penalty': 'l2',
        'loss': 'squared_hinge',
        'multi_class': 'ovr',
        'random_state': np.random.randint(100)
    }
    return Pipeline([
        ('vect', TfidfVectorizer(**tfidf_params)),
        ('clf', LinearSVC(**svc_params)),
    ])