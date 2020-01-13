import argparse
import json
from shutil import copyfile
import os


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-root', '--root-folder', required=True, type=str)
    parser.add_argument('-to', '--copy-to', required=True, type=str)
    return parser


def copy_json_images(json_dict, root_folder, copy_to):
    for image in json_dict['images']:
        file_name_from = os.path.join(root_folder, image['file_name'])
        file_name_to = os.path.join(copy_to, image['file_name'])
        copyfile(file_name_from, file_name_to)


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    copy_json_images(json_dict, args.root_folder, args.copy_to)

