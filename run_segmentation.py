import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)
import os



parser = argparse.ArgumentParser()
parser.add_argument('--segmentation_approach', type=str, default='nhpylm')
parser.add_argument('--preprocessing', type=str, default='full_melodies')
parser.add_argument('--dataset_type', type=str, default='all_antiphons')
parser.add_argument('--data_path', type=str, default='./data/cantus-corpus.csv')
parser.add_argument('--output_dir', type=str, default='./outputs/')
parser.add_argument('--seed', type=int, help='random seed', default=2)



PREDICT_SEGMENTATION = {
    "nhpylm": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: None,
    "nhpylmclasses": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: None,
    "words": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: None,
    "syllables": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: None,
    "4gram": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: None,
    "5gram": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: None,
    "6gram": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: None,
    "6gram_overlap": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: None,
    "1_7gram_overlap": lambda train_x, train_y, dev_x, dev_y, test_x, test_y: None,
}

SEGMENTATION_IGNORING_PREPROCESSING = {
    "words", "syllables"
}

PREPROCESS = {
    "full_melodies": lambda data: None,
    "intervals": lambda data: None,
    "merged_tones": lambda data: None
}

LOAD_DATASET = {
    "all_antiphons": lambda: None,
    "all_responsories": lambda: None,
    "kaug_antiphons": lambda: None,
    "kaug_responsories": lambda: None,
    "all_sci_antiphons": lambda: None, # separated cantus ids
    "all_sci_responsories": lambda: None, # separated cantus ids
}


def _store_segmentation_to_file(segmentation, file):
    content = ""
    for seg in segmentation:
        content += " ".join([segment for segment in seg]) + "\n"


def main(args):
    # load data
    chants, modes = LOAD_DATASET[args.dataset_type]()

    # split data
    train_x, train_y, dev_x, dev_y, test_x, test_y = split_dataset(chants, modes, args.seed)

    # preprocess data
    if not args.segmentation_approach in SEGMENTATION_IGNORING_PREPROCESSING:
        train_x = PREPROCESS[args.preprocessing](train_x)
        dev_x = PREPROCESS[args.preprocessing](dev_x)
        test_x = PREPROCESS[args.preprocessing](test_x)

    # segment
    train_seg, dev_seg, test_seg = PREDICT_SEGMENTATION[args.segmentation_approach](
        train_x, train_y, dev_x, dev_y, test_x, test_y
    )

    # store segmentation
    for split, seg in zip(["train", "dev", "test"], [train_seg, dev_seg, test_seg]):
        filename = f"{args.segmentation_approach}#{args.preprocessing}#{args.dataset_type}#{args.seed}#{split}.txt"
        filepath = os.path.join(args.output_dir, filename)
        _store_segmentation_to_file(seg, filepath)


if __name__ == '__main__':
    args = parser.parse_args()
    random.seed(args.seed)
    main(args)
