from decimal import Decimal, ROUND_HALF_UP
import numpy as np

def collect_chant_segment_statistics(data, key = "average_segment_lengths"):
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
        dictionary of scores of all seeds containing average_segment_lengths or uniqueness_density field
    Return
    ------
    averaged_segments: list
        averaged segment lengths of the average_segment_lengths or uniqueness_density field
    """
    segment_lists = [np.array(v[key]) for v in data.values()]

    # Find the maximum length of the segment lists
    max_length = max(len(lst) for lst in segment_lists)
    
    # Pad shorter lists with NaN for proper averaging
    padded_lists = [np.pad(lst, (0, max_length - len(lst)), constant_values=0.0) for lst in segment_lists]

    # Compute element-wise mean, ignoring NaNs
    averaged_segments = np.nanmean(padded_lists, axis=0)
    
    return list(map(float, averaged_segments.tolist()))




def get_unique_segment_densities(segmentation: list, modes: list, mode_list = ["1", "2", "3", "4", "5", "6", "7", "8"]):
    """
    Compute densities of unique segments considering each position of modes (proportionally).
    The goal is to find out if there are more unique segments at beggining, or in the middle or at the end.

    Parameters
    ----------
    segmentation : list of list of strings
        list of train chants represented as list of string segments
        [["asda", "asdasd", "as", "ds"]]
    modes : list of strings
        list of train modes
    mode_list : list of strings
        list of all unique modes we have in dataset
    Returns
    -------
    densities : dict
        dict with keys of all modes, value is always a list of 400 elements, where 
        each has a percentage (%) of that in that position of chant were unique segments
        over all chants of that mode. Index 399 stands for 100%, 199 stands for 50%, etc..
    """
    # Preprocess data
    # Dictionary of all unique segments that occure in the specific mode
    mode_unique_segments = {}
    for mode in mode_list:
        mode_unique_segments[mode] = set()
    # Collect all unique segments of all modes
    for chant, mode in zip(segmentation, modes):
        for segment in chant:
            mode_unique_segments[mode].add(segment)
    # Create the final dataframe
    unique_values = {}
    for i in range(len(mode_list)):
        temp_vocab = mode_unique_segments[mode_list[i]].copy()
        for j in range(len(mode_list)):
            if not i == j:
                for segment in mode_unique_segments[mode_list[i]]:
                    if segment in mode_unique_segments[mode_list[j]] and segment in temp_vocab:
                        temp_vocab.remove(segment)
        unique_values[mode_list[i]] = temp_vocab

    # Get Density Data
    # Prepare Density
    densities = {}
    num_chants = {}
    densities_scale = 400
    for mode in mode_list:
        num_chants[mode] = 0
        densities[mode] = np.zeros((densities_scale)) # 100% in 400 cells -> 4 cells ~ 1%
    # Get Percentage distribution of unique segments
    for chant, mode in zip(segmentation, modes):
        chant_len = len(''.join(chant))
        actual_position = 0
        tone_size = float(densities_scale)/float(chant_len)
        segment_pointer = 0
        num_chants[mode] += 1
        for i in range(1, densities_scale+1):
            while i > Decimal((actual_position + len(chant[segment_pointer]))*tone_size).quantize(0, ROUND_HALF_UP):
                actual_position += len(chant[segment_pointer])
                segment_pointer += 1
            if chant[segment_pointer] in unique_values[mode]:
                densities[mode][i-1] += 1
    for mode in mode_list:
        densities[mode] /= num_chants[mode]
        densities[mode] *= 100
    all_modes_array = np.array(list(densities.values()))  # Shape: (num_modes, 400)
    final_averaged_list = list(map(float, np.mean(all_modes_array, axis=0)))  # Shape: (400,)
    return {"uniqueness_density": final_averaged_list}



def get_average_segment_lengths_of_position(segmentation: list, modes: list, mode_list = ["1", "2", "3", "4", "5", "6", "7", "8"]):
    """
    Collect data about average semgent lenghts for the specific
    position of chant for each mode separatly.

    Parameters
    ----------
    segmentation : list of list of strings
        list of train chants represented as list of string segments
        [["asda", "asdasd", "as", "ds"]]
    modes : list of strings
        list of train modes
    mode_list : list of strings
        list of all unique modes we have in dataset
    Returns
    -------
    avg_seg_lenghts : dict
        dict with keys of all modes, value is always a list of 400 elements, where 
        each has a value of average length segment in that position over all chants 
        of that mode. Index 399 stands for 100%, 199 stands for 50%, etc..
    """
    # Preprocess data
    # Dictionary of all unique segments that occure in the specific mode
    mode_unique_segments = {}
    for mode in mode_list:
        mode_unique_segments[mode] = set()

    # Get Density Data
    # Prepare Density
    avg_seg_lenghts = {}
    num_chants = {}
    chant_scale = 400
    for mode in mode_list:
        num_chants[mode] = 0
        avg_seg_lenghts[mode] = np.zeros((chant_scale)) # 100% in 400 cells -> 4 cells ~ 1%
    # Get Percentage distribution of unique segments
    for chant, mode in zip(segmentation, modes):
        chant_len = len(''.join(chant))
        actual_position = 0
        tone_size = float(chant_scale)/float(chant_len)
        segment_pointer = 0
        num_chants[mode] += 1
        for i in range(1, chant_scale+1):
            while i > Decimal((actual_position + len(chant[segment_pointer]))*tone_size).quantize(0, ROUND_HALF_UP):
                actual_position += len(chant[segment_pointer])
                segment_pointer += 1
            avg_seg_lenghts[mode][i-1] += len(chant[segment_pointer])
    for mode in mode_list:
        avg_seg_lenghts[mode] /= num_chants[mode]
    all_modes_array = np.array(list(avg_seg_lenghts.values()))  # Shape: (num_modes, 400)
    final_averaged_list = list(map(float, np.mean(all_modes_array, axis=0)))  # Shape: (400,)
    return {"average_segment_lengths": final_averaged_list}