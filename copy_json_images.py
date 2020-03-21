import argparse
import json
from shutil import copyfile
import os
from tqdm import tqdm


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-img-fld', '--images-folder', required=True, type=str)
    parser.add_argument('-to-fld', '--copy-to-folder', required=True, type=str)
    return parser


def copy_json_images(json_dict, images_folder, copy_to_folder):
    for image in tqdm(json_dict['images']):
        file_name_from = os.path.join(images_folder, image['file_name'])
        file_name_to = os.path.join(copy_to_folder, image['file_name'])
        copyfile(file_name_from, file_name_to)


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    copy_json_images(json_dict, args.images_folder, args.copy_to_folder)

