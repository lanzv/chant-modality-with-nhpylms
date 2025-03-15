from collections import Counter
from collections import defaultdict



def compute_vocabulary_segment_length_counts(data):
    """
    Compute vocaulary segment length counts - for each length, compute how many of segments of such length are in the vocabulary.

    Parameters
    ----------
    data: list of lists of strings
        list of segmented chants represented as list of strings
    Return
    ------
    vocabulary_segment_length_counts: dict
        dict of vocabulary segment length counts, 'length: vocabulary occurences' - {"vocabulary_segment_length_counts": {3: 9, 2: 14, 1: 7, 5: 5, 6: 6, 10: 3, 4: 5, 15: 2}}
    """
    # collect vocabulary
    vocabulary = set()
    for segmented_chant in data:
        for seg in segmented_chant:
            vocabulary.add(seg)
    return {"vocabulary_segment_length_counts": dict(Counter(len(seg) for seg in vocabulary))}


def collect_vocabulay_segment_lengths(data):
    """
    Compute averaged percentage of each segment length occurence in vocabulary.

    data = {
        "1": {"vocabulary_segment_length_counts": {3: 8, 2: 12, 1: 9, 5: 6, 7: 4, 6: 4, 10: 2, 4: 4, 15: 1, 8: 1}},
        "2": {"vocabulary_segment_length_counts": {3: 6, 2: 10, 1: 10, 5: 8, 7: 2, 6: 5, 10: 1, 4: 3, 8: 2}},
        "3": {"vocabulary_segment_length_counts": {3: 9, 2: 14, 1: 7, 5: 5, 6: 6, 10: 3, 4: 5, 15: 2}},
    }

    Parameters
    ----------
    data: dict
        dictionary of scores of all seeds containing vocabulary_segment_length_counts field
    Return
    ------
    final_avg_counts: dict
        averaged and normalized content of the vocabulary_segment_length_counts field
    """
    # Compute percentages within each dictionary
    normalized_data = {}
    for seed, value in data.items():
        counts = value["vocabulary_segment_length_counts"]
        total = sum(counts.values())
        normalized_data[seed] = {k: v / total for k, v in counts.items()}

    # Compute average percentage for each length
    length_sums = defaultdict(float)

    for counts in normalized_data.values():
        for length, percentage in counts.items():
            length_sums[length] += percentage

    # Compute final average (0 is used implicitly for missing lengths)
    num_dicts = len(data)
    final_avg_counts = {length: length_sums[length] / num_dicts for length in length_sums}
    return final_avg_counts