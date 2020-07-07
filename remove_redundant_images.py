import argparse
import json
import os
from tqdm import tqdm


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-img-fld', '--images-folder', required=True, type=str)
    return parser


def remove_redundant_images(json_dict, images_folder):
    images_files = os.listdir(images_folder)
    json_images_files = [image['file_name'] for image in json_dict['images']]
    removed = 0
    for image_file in tqdm(images_files):
        if image_file not in json_images_files:
            os.remove(os.path.join(images_folder, image_file))
            removed += 1
    return removed


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    removed = remove_redundant_images(json_dict, args.images_folder)
    print('Removed {} images'.format(removed))

