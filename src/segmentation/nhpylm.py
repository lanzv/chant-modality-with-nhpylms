
from nhpylm.models import NHPYLMModel, NHPYLMClassesModel
import logging




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
    """
    # Init model
    model = NHPYLMModel(7, init_d = 0.5, init_theta = 2.0,
                    init_a = 6.0, init_b = 0.83333333,
                    beta_stops = 1.0, beta_passes = 1.0,
                    d_a = 1.0, d_b = 1.0, theta_alpha = 1.0, theta_beta = 1.0)
    # Train and Fit model
    model.train(train_x, dev_x, epochs, True, True, print_each_nth_iteration=10)
    logging.info("NHPYLM model was successfully trained.")
    # Predictions
    train_segmentation, train_perplexity = model.predict_segments(train_x)
    logging.info("Train Perplexity: {}".format(train_perplexity))
    dev_segmentation, dev_perplexity = model.predict_segments(dev_x)
    logging.info("Dev Perplexity: {}".format(dev_perplexity))
    test_segmentation, test_perplexity = model.predict_segments(test_x)
    logging.info("Test Perplexity: {}".format(test_perplexity))

    return train_segmentation, dev_segmentation, test_segmentation





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
    train_segmentation, train_perplexity, train_mode_prediction = model.predict_segments_classes(train_x)
    logging.info("Train Perplexity: {}".format(train_perplexity))
    logging.info("Train accuracy: {}".format(_compute_accuracy(train_y, train_mode_prediction)))
    dev_segmentation, dev_perplexity, dev_mode_prediction = model.predict_segments_classes(dev_x)
    logging.info("Dev Perplexity: {}".format(dev_perplexity))
    logging.info("Dev accuracy: {}".format(_compute_accuracy(dev_y, dev_mode_prediction)))
    test_segmentation, test_perplexity, test_mode_prediction = model.predict_segments_classes(test_x)
    logging.info("Test Perplexity: {}".format(test_perplexity))
    logging.info("Test accuracy: {}".format(_compute_accuracy(test_y, test_mode_prediction)))


    return train_segmentation, dev_segmentation, test_segmentation



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
