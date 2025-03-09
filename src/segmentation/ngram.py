
from src.load.segmentation import segment_kmers
from src.load.generate_data import process_volpiano


def get_ngram_segmentation(train_x, dev_x, test_x, n):
    """
    Segment clean melodies to (not overlapping) ngrams

    Parameters
    ----------
    train_x: list of strings
        list of training clean melody strings
    dev_x: list of strings
        list of dev clean melody strings
    test_x: list of strings
        list of test clean melody strings
    n: int
        ngram length
    Return
    ------
    segmented_train: list of lists of strings
        list of traing segmentations encoded as list of segments
    segmented_dev: list of lists of strings
        list of dev segmentations encoded as list of segments
    segmented_test: list of lists of strings
        list of test segmentations encoded as list of segments
    """
    segmented_train = []
    segmented_dev = []
    segmented_test = []
    for subset, subset_segmentations in zip([train_x, dev_x, test_x], [segmented_train, segmented_dev, segmented_test]):
        for notes in subset:
            ngram_segmentation = segment_kmers(notes, k=n)
            subset_segmentations.append(ngram_segmentation)
    return segmented_train, segmented_dev, segmented_test


def get_overlap_ngrams(train_x, dev_x, test_x, n):
    """
    Generate overlapping ngrams features based on clean melodies

    Parameters
    ----------
    train_x: list of strings
        list of training clean melody strings
    dev_x: list of strings
        list of dev clean melody strings
    test_x: list of strings
        list of test clean melody strings
    n: int
        ngram length
    Return
    ------
    train_features: list of lists of strings
        list of traing ngram features
    dev_features: list of lists of strings
        list of dev ngram features
    test_features: list of lists of strings
        list of test ngram features
    """
    train_features = []
    dev_features = []
    test_features = []
    for subset, subset_features in zip([train_x, dev_x, test_x], [train_features, dev_features, test_features]):
        for notes in subset:
            ngram_features = _segment_kols(notes, k=n)
            subset_features.append(ngram_features)
    return train_features, dev_features, test_features


def get_1_7overlap_ngrams(train_x, dev_x, test_x):
    """
    Generate overlapping ngrams features based on clean melodies

    Parameters
    ----------
    train_x: list of strings
        list of training clean melody strings
    dev_x: list of strings
        list of dev clean melody strings
    test_x: list of strings
        list of test clean melody strings
    n: int
        ngram length
    Return
    ------
    train_features: list of lists of strings
        list of traing ngram features
    dev_features: list of lists of strings
        list of dev ngram features
    test_features: list of lists of strings
        list of test ngram features
    """
    train_features = []
    dev_features = []
    test_features = []
    for subset, subset_features in zip([train_x, dev_x, test_x], [train_features, dev_features, test_features]):
        for notes in subset:
            new_features=[]
            for i in range(1, 8): #1, 2, 3, 4, 5, 6, 7
                new_features += _segment_kols(notes, k=i)
            subset_features.append(new_features)
    return train_features, dev_features, test_features


def _segment_kols(string: str, k: int = 1) -> list:
    chant_segments = []
    if len(string) < k:
        chant_segments.append(string)
    for i in range(0, len(string)-k+1):
        segment = string[i:i+k]
        chant_segments.append(segment)
    return chant_segments


