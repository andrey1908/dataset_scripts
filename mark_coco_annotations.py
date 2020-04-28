import argparse
import json


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-f', '--field', required=True, type=str)
    parser.add_argument('-v', '--value', required=True, type=str)
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def mark_coco_annotations(annotations, field, value):
    for ann in annotations:
        ann[field] = value


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    mark_coco_annotations(json_dict['annotations'], args.field, args.value)
    with open(args.out_file, 'w') as f:
        json.dump(json_dict, f, indent=2)

