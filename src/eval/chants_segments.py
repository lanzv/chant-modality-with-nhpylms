from decimal import Decimal, ROUND_HALF_UP
import numpy as np

def get_average_segment_lengths_of_position(segmented_chants: list):
    """
    Collect data about average semgent lenghts for the specific
    position of chant.

    Parameters
    ----------
    segmented_chants : list of list of strings
        list of train chants represented as list of string segments
        [["asda", "asdasd", "as", "ds"]]
    Returns
    -------
    avg_seg_lenghts : list
        list of 400 elements, where each has a value of average length segment in that position over all chants.
        Index 399 stands for 100%, 199 stands for 50%, etc..
    """
    # Get Density Data
    # Prepare Density
    chant_scale = 400
    avg_seg_lenghts = np.zeros((chant_scale)) # 100% in 400 cells -> 4 cells ~ 1%

    # Get Percentage distribution of unique segments
    for chant in segmented_chants:
        chant_len = len(''.join(chant))
        actual_position = 0
        tone_size = float(chant_scale)/float(chant_len)
        segment_pointer = 0
        for i in range(1, chant_scale+1):
            while i > Decimal((actual_position + len(chant[segment_pointer]))*tone_size).quantize(0, ROUND_HALF_UP):
                actual_position += len(chant[segment_pointer])
                segment_pointer += 1
            avg_seg_lenghts[i-1] += len(chant[segment_pointer])

    avg_seg_lenghts /= len(segmented_chants)
    return {"average_segment_lengths": list(map(float, avg_seg_lenghts))}





def collect_average_segment_lengths_of_position(data):
    """
    Compute averaged percentage of each segment lengths at specific chant position

    data = {
        "1": {"average_segment_lengths": [7.5 7.5 7.5 7.5 7.5 7.5 7.5 7.5 7.5 7.5 7.5 7.5 7.5 7.5 7.5 7.5 7.5 ...]},
        "2": {"average_segment_lengths": [5 3.5 3.5 3.5 4.  4.  4.  4.  4.  4.  4.  4. ...]},
        "3": {"average_segment_lengths": [4.5 6.  6.  6.  6.  6.  6.  6.  6.  6.  6.  6.  6.  6. ...]},
    }

    Parameters
    ----------
    data: dict
        dictionary of scores of all seeds containing average_segment_lengths field
    Return
    ------
    averaged_segments: list
        averaged segment lengths of the average_segment_lengths field
    """
    segment_lists = [np.array(v["average_segment_lengths"]) for v in data.values()]
    
    # Find the maximum length of the segment lists
    max_length = max(len(lst) for lst in segment_lists)
    
    # Pad shorter lists with NaN for proper averaging
    padded_lists = [np.pad(lst, (0, max_length - len(lst)), constant_values=0.0) for lst in segment_lists]

    # Compute element-wise mean, ignoring NaNs
    averaged_segments = np.nanmean(padded_lists, axis=0)
    
    return list(map(float, averaged_segments.tolist()))