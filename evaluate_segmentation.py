import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)
import os
import argparse
import random
import numpy as np
import json
import glob
from src.eval.classification_scores import svm_classification_score






parser = argparse.ArgumentParser()
parser.add_argument('--segmentation_approach', type=str, default='4gram')
parser.add_argument('--representation', type=str, default='full_melodies')
parser.add_argument('--dataset_type', type=str, default='all_antiphons')
parser.add_argument('--segmentation_dir', type=str, default='./outputs/')
parser.add_argument('--output_dir', type=str, default='./classification_scores/')
parser.add_argument('--separated_cantus_ids_split', type=bool, default=False)
parser.add_argument('--ignore_liquescents', type=bool, default=False)
parser.add_argument('--seed', type=int, help='random seed', default=0)



def _get_segmentation_paths_with_different_seeds(args):
    modes = {}
    segmentations = {}
    seeds = set()
    splits = ["train", "dev", "test"]
    other_args = ""
    if args.separated_cantus_ids_split:
        other_args += "sci"
    if args.ignore_liquescents:
        other_args += "liq"
    
    for split in splits:
        modes[split] = {}
        segmentations[split] = {}
        # Construct a search pattern with a wildcard for {seed}
        pattern = f"{args.segmentation_dir}/{args.segmentation_approach}#{args.representation}#{args.dataset_type}#*#{split}#{other_args}.txt"
        matching_files = glob.glob(pattern)
        for f in matching_files:
            segmentations[split][os.path.basename(f).split("#")[3]] = f
            seeds.add(os.path.basename(f).split("#")[3])
        # Construct a search pattern with a wildcard for {seed}
        pattern = f"{args.segmentation_dir}/modes#{args.segmentation_approach}#{args.representation}#{args.dataset_type}#*#{split}#{other_args}.txt"
        matching_files = glob.glob(pattern)
        for f in matching_files:
            modes[split][os.path.basename(f).split("#")[4]] = f
            seeds.add(os.path.basename(f).split("#")[4])

    # collect paths
    paths = {}
    for seed in seeds: 
        paths[seed] = (segmentations["train"][seed], modes["train"][seed], segmentations["dev"][seed], modes["dev"][seed], segmentations["test"][seed], modes["test"][seed])
    return paths

def _load_segmentation(train_x_path, train_y_path, dev_x_path, dev_y_path, test_x_path, test_y_path):
    # Read the segments
    train_segmentation, dev_segmentation, test_segmentation = [], [], []
    with open(train_x_path, 'r') as file:
        for line in file:
            train_segmentation.append(line.strip().split())
    with open(dev_x_path, 'r') as file:
        for line in file:
            dev_segmentation.append(line.strip().split())
    train_segmentation += dev_segmentation
    with open(test_x_path, 'r') as file:
        for line in file:
            test_segmentation.append(line.strip().split())
    
    # Read the modes
    train_modes, dev_modes, test_modes = [], [], []
    with open(train_y_path, 'r') as file:
        for line in file:
            train_modes.append(line.strip())
    with open(dev_y_path, 'r') as file:
        for line in file:
            dev_modes.append(line.strip())
    train_modes += dev_modes
    with open(test_y_path, 'r') as file:
        for line in file:
            test_modes.append(line.strip())

    return train_segmentation, train_modes, test_segmentation, test_modes


def main(args):
    scores = {}

    # get all paths relatable to the given experiment (train/dev/test, all different seeds, segmentation/modes)
    seed_paths = _get_segmentation_paths_with_different_seeds(args)

    # iterate over all different seeds
    for seed in seed_paths:
        # load segmentations
        train_x, train_y, test_x, test_y = _load_segmentation(*seed_paths[seed])
        assert len(train_x) == len(train_y)
        assert len(test_x) == len(test_y)
        logging.info("train data: {} test data: {}".format(len(train_x), len(test_x)))

        # Evaluate segmentation using bacor score
        scores[seed] = svm_classification_score(train_x, train_y, test_x, test_y)

    # collect and average scores
    f1s = []
    accuracies = []
    for seed in scores:
        f1s.append(scores[seed]["f1"])
        accuracies.append(scores[seed]["accuracy"])
    all_scores = {
        "all": scores,
        "final": {}
    }
    f1_mean, f1_std = np.mean(f1s), np.std(f1s, ddof=1)
    acc_mean, acc_std = np.mean(accuracies), np.std(accuracies, ddof=1)
    all_scores["final"]["f1"] = f1_mean
    all_scores["final"]["f1_std"] = f1_std
    all_scores["final"]["accuracy"] = acc_mean
    all_scores["final"]["accuracy_std"] = acc_std


    # Save scores
    scores_to_print = json.dumps(all_scores, indent = 4) 
    print(scores_to_print)
    other_args = ""
    if args.separated_cantus_ids_split:
        other_args += "sci"
    if args.ignore_liquescents:
        other_args += "liq"
    filename = f"{args.segmentation_approach}#{args.representation}#{args.dataset_type}#{other_args}.json"
    filepath = os.path.join(args.output_dir, filename)
    with open(filepath, 'w') as json_file:
        json.dump(all_scores, json_file, indent=4)


if __name__ == '__main__':
    args = parser.parse_args()
    random.seed(args.seed)
    main(args)
