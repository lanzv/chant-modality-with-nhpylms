from .generate_data import load_chants, filter_chants
import pandas as pd
import os
import random
import logging


def load_all_chants(chant_data_path, genre='genre_a', remove_duplicate_cantus_ids=False,
                    separated_cantus_ids_split=False, seed=0, test_ratio=0.3):
    """
    Load all chants given genre

    Parameters
    ----------
    chant_data_path: str
        path to the chant.csv file of the cantus corpus
    genre: str
        chant genre, 'genre_a' or 'genre_r'
    remove_duplicate_cantus_ids: bool
        True for removeing duplicate cantus ids, otherwise False
    separated_cantus_ids_split: bool
        when generating the train/dev/test split, group chants with same cantus ids to the same subset
    seed: int
        random seed
    Return
    ------
    volpianos: tuple of two lists
        (train_volpianos, test_volpianos), tuple of train and test volpiano features splits
    modes: tuple of two lists
        (train_modes, test_modes), tuple of train and test mode labels splits
    """
    chants_fn = os.path.join(chant_data_path)
    chants = pd.read_csv(chants_fn, index_col='id')

    # Filter chants using bacor ismir 2020 pipeline
    # we also included the liquescents removal process
    chants = filter_chants(
        chants, genre, remove_duplicate_cantus_ids=remove_duplicate_cantus_ids)

    return _split_dataset(chants, 
        separated_cantus_ids_split=separated_cantus_ids_split, 
        seed=seed, 
        test_ratio=test_ratio
    )


def load_sample_chants(chant_data_path, genre='genre_a', remove_duplicate_cantus_ids=False,
                    separated_cantus_ids_split=False, seed=0, test_ratio=0.3, sample_size=1965):
    """
    Load all chants and sample them

    Parameters
    ----------
    chant_data_path: str
        path to the chant.csv file of the cantus corpus
    genre: str
        chant genre, 'genre_a' or 'genre_r'
    remove_duplicate_cantus_ids: bool
        True for removeing duplicate cantus ids, otherwise False
    separated_cantus_ids_split: bool
        when generating the train/dev/test split, group chants with same cantus ids to the same subset
    seed: int
        random seed
    Return
    ------
    volpianos: tuple of two lists
        (train_volpianos, test_volpianos), tuple of train and test volpiano features splits
    modes: tuple of two lists
        (train_modes, test_modes), tuple of train and test mode labels splits
    """
    chants_fn = os.path.join(chant_data_path)
    chants = pd.read_csv(chants_fn, index_col='id')

    # Filter chants using bacor ismir 2020 pipeline
    # we also included the liquescents removal process
    chants = filter_chants(
        chants, genre, remove_duplicate_cantus_ids=remove_duplicate_cantus_ids)
    chants = chants.sample(n=sample_size, random_state=seed)
    
    return _split_dataset(chants, 
        separated_cantus_ids_split=separated_cantus_ids_split, 
        seed=seed, 
        test_ratio=test_ratio
    )




def load_dkaaug_chants(chant_data_path, genre='genre_a', remove_duplicate_cantus_ids=False,
                    separated_cantus_ids_split=False, seed=0, test_ratio=0.3):
    """
    Load D-KA Aug source given genre

    Parameters
    ----------
    chant_data_path: str
        path to the chant.csv file of the cantus corpus
    genre: str
        chant genre, 'genre_a' or 'genre_r'
    remove_duplicate_cantus_ids: bool
        True for removeing duplicate cantus ids, otherwise False
    separated_cantus_ids_split: bool
        when generating the train/dev/test split, group chants with same cantus ids to the same subset
    seed: int
        random seed
    Return
    ------
    volpianos: tuple of two lists
        (train_volpianos, test_volpianos), tuple of train and test volpiano features splits
    modes: tuple of two lists
        (train_modes, test_modes), tuple of train and test mode labels splits
    """
    chants_fn = os.path.join(chant_data_path)
    chants = pd.read_csv(chants_fn, index_col='id')

    # Filter chants using bacor ismir 2020 pipeline
    # we also included the liquescents removal process
    chants = filter_chants(
        chants, genre, remove_duplicate_cantus_ids=remove_duplicate_cantus_ids)
    chants = chants[chants["siglum"] == "D-KA Aug. LX"]

    return _split_dataset(chants, 
        separated_cantus_ids_split=separated_cantus_ids_split, 
        seed=seed, 
        test_ratio=test_ratio
    )


def _split_dataset(chants, separated_cantus_ids_split=False, seed=0, test_ratio=0.3):
    """
    Split chant dataset.

    Parameters
    ----------
    chants : pd.DataFrame
        The chants dataframe
    remove_duplicate_cantus_ids: bool
        True for removeing duplicate cantus ids, otherwise False
    separated_cantus_ids_split: bool
        when generating the train/dev/test split, group chants with same cantus ids to the same subset
    seed: int
        random seed
    Return
    ------
    volpianos: tuple of two lists
        (train_volpianos, test_volpianos), tuple of train and test volpiano features splits
    modes: tuple of two lists
        (train_modes, test_modes), tuple of train and test mode labels splits
    """
    random.seed(seed)

    # Extract volpiano melodies, modes and cantus ids
    volpianos = chants["volpiano"].tolist()
    modes = chants["mode"].tolist()
    cantus_ids = chants["cantus_id"].tolist()
    cantus_ids_dict = {}
    for i, cid in enumerate(cantus_ids):
        if not cid in cantus_ids_dict:
            cantus_ids_dict[cid] = []
        cantus_ids_dict[cid].append(i)


    # Determine train/test split sizes
    instances_count = len(volpianos)
    test_num = int(test_ratio * instances_count)
    train_num = instances_count - test_num

    if separated_cantus_ids_split:
        # Convert groups to a list of (cantus_id, [indices])
        cantus_groups = list(cantus_ids_dict.items())
        random.shuffle(cantus_groups)

        # Assign entire groups to test/train while keeping split sizes balanced
        train_indices, test_indices = [], []
        for cid, indices in cantus_groups:
            if len(test_indices) + len(indices) <= test_num:
                test_indices.extend(indices)
            else:
                train_indices.extend(indices)

        # Adjust if needed
        if len(test_indices) != test_num:
            logging.warning(
                f"There are {len(test_indices)}/{test_num} instances in the test set with cantus IDs not included in the train set. "
                f"{abs(test_num - len(test_indices))} instances are randomly chosen to be moved to the other split set"
                f"(it could happen that these melodies share cantus IDs with melodies from the other set)."
            )
        while len(test_indices) < test_num and train_indices:
            test_indices.append(train_indices.pop())
        while len(test_indices) > test_num:
            train_indices.append(test_indices.pop())
        assert len(test_indices) == test_num

        # Extract train/test data
        train_x = [volpianos[i] for i in train_indices]
        train_y = [modes[i] for i in train_indices]
        test_x = [volpianos[i] for i in test_indices]
        test_y = [modes[i] for i in test_indices]
    else:
        instances_list = random.sample(range(instances_count), instances_count)
        train_x, test_x = [], []
        train_y, test_y = [], []
        for i in range(test_num):
            test_x.append(volpianos[instances_list[i]])
            test_y.append(modes[instances_list[i]])
        for i in range(test_num, instances_count):
            train_x.append(volpianos[instances_list[i]])
            train_y.append(modes[instances_list[i]])


    return (train_x, test_x), (train_y, test_y)
