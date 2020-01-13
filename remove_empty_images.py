import argparse
import json
from reindex_json import reindex_json


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def only_remove_empty_images(json_dict):
    used_images = set()
    for ann in json_dict['annotations']:
        used_images.add(ann['image_id'])
    removed = 0
    for i in range(len(json_dict['images'])-1,-1,-1):
        if json_dict['images'][i]['id'] not in used_images:
            del json_dict['images'][i]
            removed += 1
    return removed


def remove_empty_images(json_dict):
    removed = only_remove_empty_images(json_dict)
    reindex_json(json_dict)
    return removed


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    removed = remove_empty_images(json_dict)
    print('Removed {} images'.format(removed))
    with open(args.out_file, 'w') as f:
        json.dump(json_dict, f, indent=2)

