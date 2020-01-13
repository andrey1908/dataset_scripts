import argparse
import json

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    return parser


def get_used_images_ids(annotations):
    used_images_ids = set()
    for annotation in annotations:
        used_images_ids.add(annotation['image_id'])
    return used_images_ids


def check_for_empty_images(json_dict):
    used_images_ids = get_used_images_ids(json_dict['annotations'])
    for image in json_dict['images']:
        if image['id'] not in used_images_ids:
            print(image['id'])


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    check_for_empty_images(json_dict)

