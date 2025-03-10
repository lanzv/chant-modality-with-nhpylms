from src.load.volpiano import volpiano_characters, expand_accidentals, clean_volpiano
from src.load.representation import interval_representation

def get_full_melodies(melodies, ignore_liquescents=False):
    """
    Extract only notes from volpianos

    Parameters
    ----------
    melodies: list of strings   
        list of volpiano melodies
    ignore_liquescents: bool
        True if we should replace all liquescents by their alternatives, False to keep them
    Return
    ------
    clean_volpianos: list of strings
        list of melodies represented as string of volpiano notes without any additional characters (like bars, '-' etc..)
    """
    clean_volpianos = []
    for volpiano in melodies:
        mel = expand_accidentals(volpiano, omit_notes=True)
        chars = volpiano_characters('liquescents', 'notes', 'flats', 'naturals') + '-'
        mel = clean_volpiano(mel, allowed_chars=chars)
        mel = mel.replace('-', '')
        if ignore_liquescents:
            mel = _replace_liquescents(mel)
        clean_volpianos.append(mel)
    return clean_volpianos



def get_merged_melodies(melodies, ignore_liquescents=False):
    """
    Extract only notes from volpianos and merge repetitive tones to one

    Parameters
    ----------
    melodies: list of strings   
        list of volpiano melodies
    ignore_liquescents: bool
        True if we should replace all liquescents by their alternatives, False to keep them
    Return
    ------
    clean_volpianos: list of strings
        list of melodies represented as string of volpiano notes without any additional characters (like bars, '-' etc..)
    """
    melodies = get_full_melodies(melodies, ignore_liquescents)
    merged_tones_melodies = []
    for mel in melodies:
        if not mel:
            merged_tones_melodies.append("")
        else:
            merged_string = mel[0]
            for char in mel[1:]:
                if char != merged_string[-1]:
                    merged_string += char
            merged_tones_melodies.append(merged_string)
    
    return merged_tones_melodies



def get_intervals(melodies):
    """
    Convert volpiano melodies to string intervals

    Parameters
    ----------
    melodies: list of strings   
        list of volpiano melodies
    Return
    ------
    intervals: list of strings
        list of melodies represented as string of intervals
    """
    melodies = get_full_melodies(melodies)
    intervals = []
    for volpiano in melodies:
        kwargs = dict(repeat_first_note=True, first_interval_empty=False,
                          segment=True, sep=' ')
        converted = interval_representation(volpiano, **kwargs)
        intervals.append(converted)    
    return intervals







def vbs2melodies(segmentations, ignore_liquescents=False):
    """
    Keep or remove liquescents of segmented melodies

    Parameters
    ----------
    segmentations: list of list of strings 
        list of segmentations which is represented as list of segments
    ignore_liquescents: bool
        True if we should replace all liquescents by their alternatives, False to keep them
    Return
    ------
    vbs_segmentations: list of list of strings
        normalized volpiano based segmentation to full melodies either with or without liquscents
    """
    vbs_segmentations = []
    for segmentation in segmentations:
        contatenated_melody = ''.join(segmentation)
        if ignore_liquescents:
            mel = _replace_liquescents(contatenated_melody)
        new_segmentation = []
        l = 0
        for seg in segmentation:
            new_segmentation.append(mel[l:l+len(seg)])
            assert len(new_segmentation[-1]) == len(seg)
            l += len(seg)
        vbs_segmentations.append(new_segmentation)
    return vbs_segmentations



def vbs2merged_melodies(segmentations, ignore_liquescents=False):
    """
    Keep or remove liquescents of segmented melodies and merge neighbouring tones to one

    Parameters
    ----------
    segmentations: list of list of strings 
        list of segmentations which is represented as list of segments
    ignore_liquescents: bool
        True if we should replace all liquescents by their alternatives, False to keep them
    Return
    ------
    vbs_segmentations_merged: list of list of strings
        normalized volpiano based segmentation to merged melodies (merged neighbouring tones) either with or without liquscents
    """
    segmentations = vbs2melodies(segmentations, ignore_liquescents)
    vbs_segmentations_merged = []
    for segmentation in segmentations:
        new_segmentation = []
        for seg in segmentation:
            if not seg:
                new_segmentation.append("")
            else:
                merged_string = seg[0]
                for char in seg[1:]:
                    if char != merged_string[-1]:
                        merged_string += char
                new_segmentation.append(merged_string)
        vbs_segmentations_merged.append(new_segmentation)
        
    return vbs_segmentations_merged



def vbs2intervals(segmentations):
    """
    Convert segmented volpiano melodies to string interval segmentation

    Parameters
    ----------
    segmentations: list of list of strings 
        list of segmentations which is represented as list of segments
    Return
    ------
    vbs_segmentations_intervals: list of list of strings
        volpiano based segmentation converted to itervals
    """
    vbs_segmentations_intervals = []
    for segmentation in segmentations:
        mel = ''.join(segmentation)
        kwargs = dict(repeat_first_note=True, first_interval_empty=False,
                          segment=True, sep=' ')
        converted = interval_representation(mel, **kwargs)
        new_segmentation = []
        l = 0
        for seg in segmentation:
            new_segmentation.append(converted[l:l+len(seg)])
            assert len(new_segmentation[-1]) == len(seg)
            l += len(seg)
        vbs_segmentations_intervals.append(new_segmentation)
    return vbs_segmentations_intervals



def _replace_liquescents(melody):
    """
    Replace liquescents by their default note alternatives

    Parameters
    ----------
    chant : str
        string of chant notes, spaces for segmenations allowed
    Returns
    -------
    basic_chant : str
        string of chant notes without liquescents
    """
    basic_chant = melody.lower()
    basic_chant = basic_chant.replace(")", "9")
    basic_chant = basic_chant.replace("(", "8")
    return basic_chant
