import os
import argparse
from utils import find_files
import json
from PIL import Image


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-img-fld', '--images-folder', required=True, type=str)
    parser.add_argument('-root-fld', '--root-folder', type=str, default='./')
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def make_coco_info(images_folder, root_folder):
    found_files, unknown_extensions = find_files(images_folder, ['.jpg', '.png'], ['.txt'])
    if len(unknown_extensions) > 0:
        print('Unknown extensions: {}'.format(unknown_extensions))
    json_dict = {'images': list(), 'annotations': list(), 'categories': list()}
    image_id = 0
    for file in found_files:
        im = Image.open(file)
        file = os.path.relpath(file, root_folder)
        image = {'file_name': file, 'width': im.width, 'height': im.height, 'id': image_id}
        json_dict['images'].append(image)
        image_id += 1
    return json_dict


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    json_dict = make_coco_info(args.images_folder, args.root_folder)
    with open(args.out_file, 'w') as f:
        json.dump(json_dict, f)
