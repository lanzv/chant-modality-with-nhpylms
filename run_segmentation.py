import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)
import os
import argparse
import random
from src.load.loader import load_all_chants, load_dkaaug_chants, load_sample_chants
from sklearn.model_selection import train_test_split
from src.preprocess.representation import get_full_melodies, get_intervals, get_merged_melodies, vbs2melodies, vbs2intervals, vbs2merged_melodies
from src.segmentation.vbs import segment_by_words, segment_by_syllables, segment_by_neumes
from src.segmentation.ngram import get_ngram_segmentation, get_overlap_ngrams, get_1_7overlap_ngrams
from src.segmentation.nhpylm import get_nhpylm_segmentation, get_nhpylmclasses_segmentation, get_nhpylm_segmentation_joint, get_nhpylmclasses_segmentation_joint

parser = argparse.ArgumentParser()
parser.add_argument('--segmentation_approach', type=str, default='nhpylm')
parser.add_argument('--representation', type=str, default='intervals')
parser.add_argument('--dataset_type', type=str, default='all_antiphons')
parser.add_argument('--data_path', type=str, default='./data/cantuscorpus-v0.2/csv/chant.csv')
parser.add_argument('--output_dir', type=str, default='./outputs/')
parser.add_argument('--separated_cantus_ids_split', type=bool, default=False)
parser.add_argument('--ignore_liquescents', type=bool, default=False)
parser.add_argument('--seed', type=int, help='random seed', default=2)



PREDICT_SEGMENTATION = {
    "nhpylm": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: get_nhpylm_segmentation(
        train_x, dev_x, test_x, epochs=200
    ),
    "nhpylmclasses": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: get_nhpylmclasses_segmentation(
        train_x, train_y, dev_x, dev_y, test_x, test_y, epochs=200
    ),    
    "nhpylm_joint": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: get_nhpylm_segmentation_joint(
        train_x, dev_x, test_x, epochs=200
    ),
    "nhpylmclasses_joint": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: get_nhpylmclasses_segmentation_joint(
        train_x, train_y, dev_x, dev_y, test_x, test_y, epochs=200
    ),
    "words": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: segment_by_words(
        train_x, dev_x, test_x
    ),
    "syllables": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: segment_by_syllables(
        train_x, dev_x, test_x
    ),
    "neumes": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: segment_by_neumes(
        train_x, dev_x, test_x
    ),
    "4gram": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: get_ngram_segmentation(
        train_x, dev_x, test_x, n=4
    ),
    "5gram": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: get_ngram_segmentation(
        train_x, dev_x, test_x, n=5
    ),
    "6gram": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: get_ngram_segmentation(
        train_x, dev_x, test_x, n=6
    ),
    "6gram_overlap": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: get_overlap_ngrams(
        train_x, dev_x, test_x, n=6
    ),
    "1_7gram_overlap": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: get_1_7overlap_ngrams(
        train_x, dev_x, test_x
    ),
}

VOLPIANO_BASED_SEGMENTATION = {
    "words", "syllables", "neumes"
}

REPRESENTATIONS = {
    "full_melodies": lambda data, ignore_liquescents: get_full_melodies(data, ignore_liquescents),
    "intervals": lambda data, ignore_liquescents: get_intervals(data),
    "merged_tones": lambda data, ignore_liquescents: get_merged_melodies(data, ignore_liquescents),
}

VOLPIANO_BASED_SEGS_REPRESENTATIONS = {
    "full_melodies": lambda data, ignore_liquescents: vbs2melodies(data, ignore_liquescents),
    "intervals": lambda data, ignore_liquescents: vbs2intervals(data),
    "merged_tones": lambda data, ignore_liquescents: vbs2merged_melodies(data, ignore_liquescents),
}

LOAD_DATASET = {
    "all_antiphons": lambda chant_data_path, separated_cantus_ids_split, seed: load_all_chants(
        chant_data_path, "genre_a", False, separated_cantus_ids_split, seed=seed),
    "all_responsories": lambda chant_data_path, separated_cantus_ids_split, seed: load_all_chants(
        chant_data_path, "genre_r", False, separated_cantus_ids_split, seed=seed),
    "dkaaug_antiphons": lambda chant_data_path, separated_cantus_ids_split, seed: load_dkaaug_chants(
        chant_data_path, "genre_a", False, separated_cantus_ids_split, seed=seed),
    "dkaaug_responsories": lambda chant_data_path, separated_cantus_ids_split, seed: load_dkaaug_chants(
        chant_data_path, "genre_r", False, separated_cantus_ids_split, seed=seed),
    "sampled_antiphons": lambda chant_data_path, separated_cantus_ids_split, seed: load_sample_chants(
        chant_data_path, "genre_a", False, separated_cantus_ids_split, seed=seed, sample_size=1965),
    "sampled_responsories": lambda chant_data_path, separated_cantus_ids_split, seed: load_sample_chants(
        chant_data_path, "genre_r", False, separated_cantus_ids_split, seed=seed, sample_size=907),
}


def _store_segmentation_to_file(segmentation, file):
    lines = []
    for seg in segmentation:
        lines.append(" ".join([segment for segment in seg]))
    if os.path.exists(file):
        os.remove(file)
    with open(file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def _store_modes_to_file(modes, file):
    if os.path.exists(file):
        os.remove(file)
    with open(file, "w", encoding="utf-8") as f:
        f.write("\n".join(modes))


def main(args):
    # load data
    chants, modes = LOAD_DATASET[args.dataset_type](
        args.data_path, args.separated_cantus_ids_split, args.seed)
    train_x, test_x = chants
    train_y, test_y = modes

    # dev split
    train_x, dev_x, train_y, dev_y = train_test_split(
        train_x, train_y, test_size=0.1, random_state=args.seed, shuffle=True
    )

    logging.info("train data: {} dev data: {} test data: {}".format(len(train_x), len(dev_x), len(test_x)))

    # preprocess data
    if not args.segmentation_approach in VOLPIANO_BASED_SEGMENTATION:
        train_x = REPRESENTATIONS[args.representation](train_x, args.ignore_liquescents)
        dev_x = REPRESENTATIONS[args.representation](dev_x, args.ignore_liquescents)
        test_x = REPRESENTATIONS[args.representation](test_x, args.ignore_liquescents)
 

    # segment
    train_seg, dev_seg, test_seg, scores = PREDICT_SEGMENTATION[args.segmentation_approach](
        train_x, train_y, dev_x, dev_y, test_x, test_y
    )

    if args.segmentation_approach in VOLPIANO_BASED_SEGMENTATION:
        train_seg = VOLPIANO_BASED_SEGS_REPRESENTATIONS[args.representation](train_seg, args.ignore_liquescents)
        dev_seg = VOLPIANO_BASED_SEGS_REPRESENTATIONS[args.representation](dev_seg, args.ignore_liquescents)
        test_seg = VOLPIANO_BASED_SEGS_REPRESENTATIONS[args.representation](test_seg, args.ignore_liquescents)

    # store segmentation
    for split, seg, modes in zip(["train", "dev", "test"], [train_seg, dev_seg, test_seg], [train_y, dev_y, test_y]):
        other_args = ""
        if args.separated_cantus_ids_split:
            other_args += "sci"
        if args.ignore_liquescents:
            other_args += "liq"
        filename = f"{args.segmentation_approach}#{args.representation}#{args.dataset_type}#{args.seed}#{split}#{other_args}.txt"
        filepath = os.path.join(args.output_dir, filename)
        _store_segmentation_to_file(seg, filepath)
        filepath = os.path.join(args.output_dir, "modes#"+filename)
        _store_modes_to_file(modes, filepath)
    
    # store scores if there are any
    if not scores == None:
        other_args = ""
        if args.separated_cantus_ids_split:
            other_args += "sci"
        if args.ignore_liquescents:
            other_args += "liq"
        filename = f"{args.segmentation_approach}#{args.representation}#{args.dataset_type}#{args.seed}#score#{other_args}.json"
        filepath = os.path.join(args.output_dir, filename)

        with open(filepath, 'w') as json_file:
            json.dump(scores, json_file, indent=4)




if __name__ == '__main__':
    args = parser.parse_args()
    random.seed(args.seed)
    main(args)
