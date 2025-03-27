import nltk
from nltk.lm import KneserNeyInterpolated
from nltk.lm.preprocessing import padded_everygram_pipeline
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('punkt_tab')


def compute_kni_perplexity(train_segmentation, dev_segmentation, test_segmentation, n=2, d=0.5):
    """
    Compute Perplexity of test segmentation using Kneser Ney Interpolated smoothing 
    Dev segmentation is used mainly for representing the <UNK> token during training

    Parameters
    ----------
    train_segmentation: list of strings
        list of train segmentations represented as strings, sequences of segments separated by spaces
    dev_segmentation: list of strings
        list of dev segmentations represented as strings, sequences of segments separated by spaces
    test_segmentation: list of strings
        list of test segmentations represented as strings, sequences of segments separated by spaces
    n: int
        number of n-grams (by default bigram for n=2)
    d: float
        discout factor
    Returns
    -------
    kni_perplexity_dict: dict
        dictionary of key 'kni_perplexity' with the value of perplexity on test set
    """
    tokenized_segmentations = [word_tokenize(seg) for seg in train_segmentation]

    vocab = {'<s>', '</s>', '<UNK>'}
    for segmentation in train_segmentation:
        for seg in segmentation:
            vocab.add(seg)
    dev_tokenized_segmentations = [word_tokenize(seg) for seg in dev_segmentation]
    dev_tokenized_segmentations = [_replace_unk(tokens, vocab) for tokens in dev_tokenized_segmentations]

    tokenized_segmentations += dev_tokenized_segmentations
    train_data, padded_sents = padded_everygram_pipeline(n, tokenized_segmentations)
    model = KneserNeyInterpolated(n, discount=d)
    model.fit(train_data, padded_sents)

    avg_perplexity = _compute_perplexity_for_sequences(model, test_segmentation, n)
    return {"kni_perplexity": avg_perplexity}


def _compute_perplexity_for_sequences(model, sequences, n=2):
    """
    Compute perplexity for testing sequences for the given model

    Parameters
    ----------
    model: nltk.lm model
        language model from NLTK library, for instance the KneserNeyInterpolated model
    sequences: list of strings
        list of test segmentations represented as strings, sequences of segments separated by spaces
    n: int
        number of n-grams (by default bigram for n=2)
    Return
    ------
    avg_perplexity: float
        perplexity of all sequences
    """
    vocab = model.vocab
    perplexities = []
    for sequence in sequences:
        tokens = word_tokenize(sequence)
        tokens = _replace_unk(tokens, vocab)
        test_data_ngrams, tokens = padded_everygram_pipeline(n, [tokens])
        test_ngrams = list(nltk.ngrams(list(tokens), n))
        perplexity = model.perplexity(test_ngrams)
        perplexities.append(perplexity)

    avg_perplexity = sum(perplexities) / len(perplexities) if perplexities else float('inf')
    return avg_perplexity


def _replace_unk(tokens, vocab):
    """
    Replace all tokens that are not included in vocab vocabulay by '<UNK>' token
    """
    return [token if token in vocab else '<UNK>' for token in tokens]
