from src.load.segmentation import segment_words, segment_syllables, segment_neumes
from src.load.generate_data import process_volpiano

# Volpiano Based Segmentations (VBS)

def segment_by_words(train_x, dev_x, test_x):
    """
    Segment melodies encoded in volpiano by words

    Parameters
    ----------
    train_x: list of strings
        list of training volpiano melody strings
    dev_x: list of strings
        list of dev volpiano melody strings
    test_x: list of strings
        list of test volpiano melody strings
    Return
    ------
    segmented_train: list of list of strings
        list of traing segmentations encoded as list of segments
    segmented_dev: list of list of strings
        list of dev segmentations encoded as list of segments
    segmented_test: list of list of strings
        list of test segmentations encoded as list of segments
    scores: None
        the score is not supported here
    """
    segmented_train = []
    segmented_dev = []
    segmented_test = []
    for subset, subset_segmentations in zip([train_x, dev_x, test_x], [segmented_train, segmented_dev, segmented_test]):
        for volpiano in subset:
            clean_volpiano = process_volpiano(volpiano)
            word_segmentation = segment_words(clean_volpiano)
            subset_segmentations.append(word_segmentation)
    return segmented_train, segmented_dev, segmented_test, None


def segment_by_syllables(train_x, dev_x, test_x):
    """
    Segment melodies encoded in volpiano by syllables

    Parameters
    ----------
    train_x: list of strings
        list of training volpiano melody strings
    dev_x: list of strings
        list of dev volpiano melody strings
    test_x: list of strings
        list of test volpiano melody strings
    Return
    ------
    segmented_train: list of list of strings
        list of traing segmentations encoded as list of segments
    segmented_dev: list of list of strings
        list of dev segmentations encoded as list of segments
    segmented_test: list of list of strings
        list of test segmentations encoded as list of segments
    scores: None
        the score is not supported here
    """
    segmented_train = []
    segmented_dev = []
    segmented_test = []
    for subset, subset_segmentations in zip([train_x, dev_x, test_x], [segmented_train, segmented_dev, segmented_test]):
        for volpiano in subset:
            clean_volpiano = process_volpiano(volpiano)
            word_segmentation = segment_syllables(clean_volpiano)
            subset_segmentations.append(word_segmentation)
    return segmented_train, segmented_dev, segmented_test, None


def segment_by_neumes(train_x, dev_x, test_x):
    """
    Segment melodies encoded in volpiano by neumes

    Parameters
    ----------
    train_x: list of strings
        list of training volpiano melody strings
    dev_x: list of strings
        list of dev volpiano melody strings
    test_x: list of strings
        list of test volpiano melody strings
    Return
    ------
    segmented_train: list of list of strings
        list of traing segmentations encoded as list of segments
    segmented_dev: list of list of strings
        list of dev segmentations encoded as list of segments
    segmented_test: list of list of strings
        list of test segmentations encoded as list of segments
    scores: None
        the score is not supported here
    """
    segmented_train = []
    segmented_dev = []
    segmented_test = []
    for subset, subset_segmentations in zip([train_x, dev_x, test_x], [segmented_train, segmented_dev, segmented_test]):
        for volpiano in subset:
            clean_volpiano = process_volpiano(volpiano)
            word_segmentation = segment_neumes(clean_volpiano)
            subset_segmentations.append(word_segmentation)
    return segmented_train, segmented_dev, segmented_test, None