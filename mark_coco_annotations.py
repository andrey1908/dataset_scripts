import argparse
import json


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-f', '--field', required=True, type=str)
    parser.add_argument('-v', '--value', required=True, type=str)
    parser.add_argument('--force', action='store_true')
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def mark_coco_annotations(annotations, field, value, force=False):
    for ann in annotations:
        if (field in ann.keys()) and not force:
            raise RuntimeError('Use --force to overwrite information.')
    for ann in annotations:
        ann[field] = eval(value)


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    print(type(eval(args.value)))
    mark_coco_annotations(json_dict['annotations'], args.field, args.value, args.force)
    with open(args.out_file, 'w') as f:
        json.dump(json_dict, f, indent=2)

