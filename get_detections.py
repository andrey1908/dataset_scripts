import argparse
import json


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def get_detections(json_dict):
    return json_dict['annotations']


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    detections = get_detections(json_dict)
    with open(args.out_file, 'w') as f:
        json.dump(detections, f, indent=2)

