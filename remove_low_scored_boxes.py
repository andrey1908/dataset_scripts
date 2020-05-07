import argparse
import json
from utils.coco_tools import leave_annotations


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-thr', '--threshold', required=True, type=float)
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def remove_low_scored_boxes(json_dict, threshold):
    idxs_to_leave = list()
    for i in range(len(json_dict['annotations'])):
        if json_dict['annotations'][i]['score'] >= threshold:
            idxs_to_leave.append(i)
    removed = len(json_dict['annotations']) - len(idxs_to_leave)
    leave_annotations(json_dict['annotations'], idxs_to_leave)
    return removed


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    removed = remove_low_scored_boxes(json_dict, args.threshold)
    print('Removed {} boxes'.format(removed))
    with open(args.out_file, 'w') as f:
        json.dump(json_dict, f, indent=2)

