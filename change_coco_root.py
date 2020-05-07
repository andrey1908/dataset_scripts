import argparse
import json
import os


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-root', '--root-folder', required=True, type=str)
    parser.add_argument('-new-root', '--new-root-folder', required=True, type=str)
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def change_coco_root(json_dict, root_folder, new_root_folder):
    for image in json_dict['images']:
        file_name = image['file_name']
        new_file_name = os.path.relpath(os.path.join(root_folder, file_name), new_root_folder)
        image['file_name'] = new_file_name


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    change_coco_root(json_dict, args.root_folder, args.new_root_folder)
    with open(args.out_file, 'w') as f:
        json.dump(json_dict, f, indent=2)

