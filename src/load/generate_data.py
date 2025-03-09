# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Author: Bas Cornelissen
# Copyright © 2019 Bas Cornelissen
# License: MIT
# -----------------------------------------------------------------------------
"""
Data generation
===============

This script reads out the raw Cantus data (not included in the repository) and
generates the datasets used in this study. We have different datasets for
different genres, and each comes in two variants (full and subset). For 
example:

* `responsory/full/`: a dataset of responsories 
* `responsory/subset/`: a subset where we made sure that every chant had a 
unique (cantus_id, mode) combination. This effectively means there are no (or 
in any case fewer) melody variants in the corpus.

The script is completely deterministic: all random seeds have been fixed. We 
also verified that two independent runs resulted in identical datasets (we log
md5 hashes of the generated files). However, all randomness is determined by 
one global random state, to be able to generate independent datasets for use
in independent runs.

Note that this script is a little slow. Generating the `responsory/full`
dataset for example takes around 2 minutes. (It could be further optimized, 
but there is no need to run it often.)

usage: `python -m src.generate_data [--what=demo/complete]`
"""
import os
import glob
import logging
import numpy as np
import pandas as pd

from .filters import *
from .segmentation import *
from .representation import *
from .volpiano import volpiano_characters
from .volpiano import expand_accidentals
from .volpiano import clean_volpiano
from .features import initial
from .features import final
from .features import lowest
from .features import highest
from .features import ambitus
from .features import initial_gesture
from .features import pitch_profile
from .features import pitch_class_profile
from .features import repetition_profile

CUR_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(CUR_DIR, os.path.pardir))
CANTUS_DIR = os.path.join(ROOT_DIR, 'cantuscorpus', 'csv')


def load_chants(cantus_dir: str = CANTUS_DIR, demo: bool = False):
    """Load CantusCorpus chants data

    Parameters
    ----------
    cantus_dir : str
        The directory where all Cantus data is stored. Defaults to the 
        `cantus-data` directory in the root of this repository.
    demo : bool, default False
        Load the demo data? This is a small random subset of 100 chants
        for development purposes.

    Returns
    -------
    pd.DataFrame
        The chants
    """
    if demo:
        demo_fn = os.path.join(cantus_dir, 'chant-demo-sample.csv')
        chants = pd.read_csv(demo_fn, index_col='id')
    else:
        chants_fn = os.path.join(cantus_dir, 'chant.csv')
        chants = pd.read_csv(chants_fn, index_col='id')
    return chants

def filter_chants(chants: pd.DataFrame, genre: str,
    remove_duplicate_cantus_ids: bool) -> pd.DataFrame:
    """Filter out only complete, clean chants

    Parameters
    ----------
    chants : pd.DataFrame
        The chants dataframe
    genre : str
        The chant genre to include

    Returns
    -------
    pd.DataFrame
        A filtered dataframe of chants
    """
    opts = dict(logger=lambda msg: logging.info(f' . {msg}'))
    chants = filter_chants_without_volpiano(chants, **opts)
    chants = filter_chants_without_notes(chants, **opts)
    chants = filter_chants_without_simple_mode(
        chants, include_transposed=False, **opts)
    chants = filter_chants_without_full_text(chants, **opts)
    chants = filter_chants_where_incipit_is_full_text(chants, **opts)
    chants = filter_chants_by_genre(chants, include=[genre], **opts)

    chants = filter_chants_not_starting_with_G_clef(chants, **opts)
    chants = filter_chants_with_F_clef(chants, **opts)
    chants = filter_chants_with_missing_pitches(chants, **opts)
    chants = filter_chants_with_nonvolpiano_chars(chants, **opts)
    chants = filter_chants_without_word_boundary(chants, **opts)

    chants = filter_chants_with_duplicated_notes(chants, **opts)
    if remove_duplicate_cantus_ids:
        chants = sample_one_chant_per_mode_and_cantus_id(
            chants, random_state=np.random.randint(100), **opts)
    return chants

def process_volpiano(volpiano: str) -> str:
    """Clean up a volpiano string.

    First, it expands all accidentals, while omitting notes. That means that
    instead of for example `ij` for a b-flat, the accidental `i` is used to 
    represent the b-flat.
    
    Second, all characters that do not represent notes, liquescents, flats, 
    naturals, or boundaries (dashes) are removed. This results in a clean 
    volpiano string with only notes and boundaries.

    Parameters
    ----------
    volpiano : str
        A volpiano string

    Returns
    -------
    str
        The cleaned up volpiano string
    """
    volpiano = expand_accidentals(volpiano, omit_notes=True)
    chars = volpiano_characters('liquescents', 'notes', 'flats', 'naturals') + '-'
    volpiano = clean_volpiano(volpiano, allowed_chars=chars)
    return volpiano

def get_segmentations(chants: pd.DataFrame, k_min: int = 1, k_max: int = 16, 
                  sep: str = ' ') -> pd.DataFrame:
    """Generate all segmentations of the volpiano strings in a dataframe

    Parameters
    ----------
    chants : pd.DataFrame
        The chants dataframe with a `volpiano` column
    k_min : int, by default 1
        Length of the smallest k-mer segmentation
    k_max : int, by default 8
        Length of the largest k-mer segmentation
    sep : str, by default ' '
        The separator string to use

    Returns
    -------
    pd.DataFrame
        A dataframe with columns `words`, `syllables`, `neumes`, `k-mer` for
        each k_min <= k <= k_max, and `poisson` containing segmented volpiano
        strings.
    """
    # Helper function to join the segments
    join = lambda segments: sep.join(segments)

    # Clean up volpiano
    volpiano = chants.volpiano.map(process_volpiano)
    notes = volpiano.str.replace('-', '')
    
    # Natural segmentations
    df = pd.DataFrame(index=chants.index)
    df['words'] = volpiano.map(segment_words).map(join)
    df['syllables'] = volpiano.map(segment_syllables).map(join)
    df['neumes'] = volpiano.map(segment_neumes).map(join)
    
    # Baselines
    for k in range(k_min, k_max+1):
        kmer_segmenter = lambda vol: segment_kmers(vol, k=k)
        df[f'{k}-mer'] = notes.map(kmer_segmenter).map(join)
    poisson_segmenter_3 = lambda vol: segment_poisson(vol, lam=3)
    df['poisson-3'] = notes.map(poisson_segmenter_3).map(join)
    poisson_segmenter_5 = lambda vol: segment_poisson(vol, lam=5)
    df['poisson-5'] = notes.map(poisson_segmenter_5).map(join)
    poisson_segmenter_7 = lambda vol: segment_poisson(vol, lam=7)
    df['poisson-7'] = notes.map(poisson_segmenter_7).map(join)

    return df

def get_representation(segments, representation, dependent):
    """Convert the representation of segmented volpiano strings

    Parameters
    ----------
    segments : pd.DataFrame
        A dataframe where every column contains volpiano strings segmented by
        spaces.
    representation : { 'contour', 'interval' }
        The representation to convert to
    dependent : bool
        Convert to a dependent representation?

    Returns
    -------
    pd.DataFrame
        A dataframe of the same form, but now all volpiano strings have been
        converted to the target representation
    """
    df = pd.DataFrame(index=segments.index)

    if representation == 'contour':
        converter_fn = contour_representation
    elif representation == 'interval':
        converter_fn = interval_representation

    for col in segments.columns:
        values = segments[col]
        
        # Dependent representation:
        # Compute a relative representation of the entire chant directly,
        # but repeat the first note to ensure the length is the same.
        if dependent:
            kwargs = dict(repeat_first_note=True, first_interval_empty=False,
                          segment=True, sep=' ')
            converted = [converter_fn(volpiano, **kwargs) for volpiano in values]
        
        # Independent representation
        # First split the volpiano in units, and then compute the relative 
        # representation of each of the units.
        else:
            kwargs = dict(repeat_first_note=False, first_interval_empty=True, 
                          segment=True, sep=' ')
            converted = []
            for volpiano in values:
                units = volpiano.split(' ')
                conv_units = [converter_fn(unit, **kwargs) for unit in units]
                converted.append(' '.join(conv_units))
        df[col] = converted
    return df

def get_features(chants: pd.DataFrame) -> pd.DataFrame:
    """Extract features from a chants dataframe

    Parameters
    ----------
    chants : pd.DataFrame
        The chants dataframe

    Returns
    -------
    pd.DataFrame
        A dataframe with one feature per column
    """
    df = pd.DataFrame(index=chants.index)
    volpiano = chants.volpiano.map(process_volpiano)
    notes = volpiano.str.replace('-', '')
    pitches = notes.map(volpiano_to_midi)

    df['initial'] = pitches.map(initial)
    df['final'] = pitches.map(final)
    df['lowest'] = pitches.map(lowest)
    df['highest'] = pitches.map(highest)
    df['ambitus'] = pitches.map(ambitus)
    
    init_gestures = np.array(pitches.map(initial_gesture).to_list())
    for i in range(init_gestures.shape[1]):
        df[f'initial_gesture_{i+1}'] = init_gestures[:, i]

    pitch_profiles = np.array(pitches.map(pitch_profile).to_list())
    for i in range(pitch_profiles.shape[1]):
        df[f'freq_MIDI_{MIN_MIDI_PITCH+i}'] = pitch_profiles[:, i]

    pitch_class_profiles = np.array(pitches.map(pitch_class_profile).to_list())
    for i in range(pitch_class_profiles.shape[1]):
        df[f'freq_pitch_class_{i}'] = pitch_class_profiles[:, i]

    repetition_profiles = np.array(pitches.map(repetition_profile).to_list())
    for i in range(repetition_profiles.shape[1]):
        df[f'repetition_score_MIDI_{MIN_MIDI_PITCH+i}'] = repetition_profiles[:, i]

    return df
