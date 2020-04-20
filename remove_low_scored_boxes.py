import argparse
import json


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-thr', '--threshold', required=True, type=float)
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def remove_low_scored_boxes(json_dict, threshold):
    sub = 0
    ann_id = 1
    for i in range(len(json_dict['annotations'])):
        if json_dict['annotations'][i - sub]['score'] < threshold:
            del json_dict['annotations'][i - sub]
            sub += 1
        else:
            json_dict['annotations'][i - sub]['id'] = ann_id
            ann_id += 1
    return sub


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    removed = remove_low_scored_boxes(json_dict, args.threshold)
    print('Removed {} boxes'.format(removed))
    with open(args.out_file, 'w') as f:
        json.dump(json_dict, f, indent=2)

