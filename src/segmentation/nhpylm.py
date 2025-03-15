
from nhpylm.models import NHPYLMModel, NHPYLMClassesModel
import logging
from sklearn.metrics import f1_score
import json



def get_nhpylm_segmentation(train_x, dev_x, test_x, epochs=200):
    """
    Segment melodies using nhpylm model

    Parameters
    ----------
    train_x: list of strings
        list of training clean melody strings
    dev_x: list of strings
        list of dev clean melody strings
    test_x: list of strings
        list of test clean melody strings
    epochs: int
        number of nhpylm training iterations
    Return
    ------
    train_segmentation: list of lists of strings
        list of traing segmentations encoded as list of segments
    dev_segmentation: list of lists of strings
        list of dev segmentations encoded as list of segments
    test_segmentation: list of lists of strings
        list of test segmentations encoded as list of segments
    scores: dict
        dictionary of scores
    """
    # Init model
    model = NHPYLMModel(7, init_d = 0.5, init_theta = 2.0,
                    init_a = 6.0, init_b = 0.83333333,
                    beta_stops = 1.0, beta_passes = 1.0,
                    d_a = 1.0, d_b = 1.0, theta_alpha = 1.0, theta_beta = 1.0)
    # Train and Fit model
    model.train(train_x, dev_x, epochs, True, True, print_each_nth_iteration=10)
    logging.info("NHPYLM model was successfully trained.")
    scores = {"train": {}, "dev": {}, "test": {}}
    # Predictions
    scores
    train_segmentation, train_perplexity = model.predict_segments(train_x)
    scores["train"]["perplexity"] = train_perplexity
    logging.info("Train Perplexity: {}".format(train_perplexity))
    dev_segmentation, dev_perplexity = model.predict_segments(dev_x)
    scores["dev"]["perplexity"] = dev_perplexity
    logging.info("Dev Perplexity: {}".format(dev_perplexity))
    test_segmentation, test_perplexity = model.predict_segments(test_x)
    scores["test"]["perplexity"] = test_perplexity
    logging.info("Test Perplexity: {}".format(test_perplexity))

    logging.info("Evaluation Scores:\n{}".format(json.dumps(scores, indent=4)))

    return train_segmentation, dev_segmentation, test_segmentation, scores





def get_nhpylm_segmentation_joint(train_x, dev_x, test_x, epochs=200):
    """
    Segment melodies using nhpylm model, use all data for training
    (train_x = train_x + dev_x + test_x)

    Parameters
    ----------
    train_x: list of strings
        list of training clean melody strings
    dev_x: list of strings
        list of dev clean melody strings
    test_x: list of strings
        list of test clean melody strings
    epochs: int
        number of nhpylm training iterations
    Return
    ------
    train_segmentation: list of lists of strings
        list of traing segmentations encoded as list of segments
    dev_segmentation: list of lists of strings
        list of dev segmentations encoded as list of segments
    test_segmentation: list of lists of strings
        list of test segmentations encoded as list of segments
    scores: dict
        dictionary of scores
    """
    train_x += dev_x
    train_x += test_x
    return get_nhpylm_segmentation(train_x, dev_x, test_x, epochs)



def get_nhpylmclasses_segmentation(train_x, train_y, dev_x, dev_y, test_x, test_y, epochs=200):
    """
    Segment melodies using nhpylm classes model + predict modes

    Parameters
    ----------
    train_x: list of strings
        list of training clean melody strings
    dev_x: list of strings
        list of dev clean melody strings
    test_x: list of strings
        list of test clean melody strings
    epochs: int
        number of nhpylm training iterations
    Return
    ------
    train_segmentation: list of lists of strings
        list of traing segmentations encoded as list of segments
    dev_segmentation: list of lists of strings
        list of dev segmentations encoded as list of segments
    test_segmentation: list of lists of strings
        list of test segmentations encoded as list of segments
    scores: dict
        dictionary of scores
    """
    # Init model
    model = NHPYLMClassesModel(7, init_d = 0.5, init_theta = 2.0,
                    init_a = 6.0, init_b = 0.83333333,
                    beta_stops = 1.0, beta_passes = 1.0,
                    d_a = 1.0, d_b = 1.0, theta_alpha = 1.0, theta_beta = 1.0)
    # Train and Fit model
    model.train(train_x, dev_x, train_y, dev_y, epochs, True, True, print_each_nth_iteration=10)
    logging.info("NHPYLMClasses model was successfully trained.")

    # Predictions
    scores = {"train": {}, "dev": {}, "test": {}}
    train_segmentation, train_perplexity, train_mode_prediction = model.predict_segments_classes(train_x)
    train_accuracy = _compute_accuracy(train_y, train_mode_prediction)
    train_f1 = f1_score(train_y, train_mode_prediction, average='weighted')
    scores["train"]["perplexity"] = train_perplexity
    scores["train"]["accuracy"] = train_accuracy
    scores["train"]["f1"] = train_f1
    logging.info("Train Perplexity: {}".format(train_perplexity))
    logging.info("Train Accuracy: {}".format(train_accuracy))
    logging.info("Train F1: {}".format(train_f1))

    dev_segmentation, dev_perplexity, dev_mode_prediction = model.predict_segments_classes(dev_x)
    dev_accuracy = _compute_accuracy(dev_y, dev_mode_prediction)
    dev_f1 = f1_score(dev_y, dev_mode_prediction, average='weighted')
    scores["dev"]["perplexity"] = dev_perplexity
    scores["dev"]["accuracy"] = dev_accuracy
    scores["dev"]["f1"] = dev_f1
    logging.info("Dev Perplexity: {}".format(dev_perplexity))
    logging.info("Dev Accuracy: {}".format(dev_accuracy))
    logging.info("Dev F1: {}".format(dev_f1))


    test_segmentation, test_perplexity, test_mode_prediction = model.predict_segments_classes(test_x)
    test_accuracy = _compute_accuracy(test_y, test_mode_prediction)
    test_f1 = f1_score(test_y, test_mode_prediction, average='weighted')
    scores["test"]["perplexity"] = test_perplexity
    scores["test"]["accuracy"] = test_accuracy
    scores["test"]["f1"] = test_f1
    logging.info("Test Perplexity: {}".format(test_perplexity))
    logging.info("Test Accuracy: {}".format(test_accuracy))
    logging.info("Test F1: {}".format(test_f1))

    logging.info("Evaluation Scores:\n{}".format(json.dumps(scores, indent=4)))

    return train_segmentation, dev_segmentation, test_segmentation, scores



def get_nhpylmclasses_segmentation_joint(train_x, train_y, dev_x, dev_y, test_x, test_y, epochs=200):
    """
    Segment melodies using nhpylm classes model + predict modes, use all data for training
    (train_x = train_x + dev_x + test_x)

    Parameters
    ----------
    train_x: list of strings
        list of training clean melody strings
    dev_x: list of strings
        list of dev clean melody strings
    test_x: list of strings
        list of test clean melody strings
    epochs: int
        number of nhpylm training iterations
    Return
    ------
    train_segmentation: list of lists of strings
        list of traing segmentations encoded as list of segments
    dev_segmentation: list of lists of strings
        list of dev segmentations encoded as list of segments
    test_segmentation: list of lists of strings
        list of test segmentations encoded as list of segments
    scores: dict
        dictionary of scores
    """
    train_x += dev_x
    train_x += test_x
    train_y += dev_y
    train_y += test_y
    return get_nhpylmclasses_segmentation(train_x, train_y, dev_x, dev_y, test_x, test_y, epochs=epochs)


def _compute_accuracy(gold_modes, predicted_modes):
    """
    compute accuracy

    Parameters
    ----------
    gold_modes: list of strings
        gold lables of modes
    predicted_modes: list of strings
        mode predictions
    Return
    ------
    accuracy: float
        accuracy
    """
    correct = 0.0
    for g, p in zip(gold_modes, predicted_modes):
        if g == p:
            correct += 1.0
    return correct/len(gold_modes)
