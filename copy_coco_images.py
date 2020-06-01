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
    parser.add_argument('-ml', '--make-links', action='store_true')
    parser.add_argument('-co', '--copy-ok', action='store_true')
    return parser


def copy_coco_images(json_dict, images_folder, copy_to_folder, make_links=False, copy_ok=False):
    making_link_errors_num = 0
    for image in tqdm(json_dict['images']):
        file_name_from = os.path.join(images_folder, image['file_name'])
        file_name_to = os.path.join(copy_to_folder, image['file_name'])
        if make_links:
            try:
                os.link(file_name_from, file_name_to)
            except:
                if copy_ok:
                    copyfile(file_name_from, file_name_to)
                    making_link_errors_num += 1
                else:
                    raise RuntimeError('Could not make link for {} (consider using --copy-ok)'.format(file_name_from))
        else:
            copyfile(file_name_from, file_name_to)
    if make_links and (making_link_errors_num > 0):
        print('Could not make {} of {} links'.format(making_link_errors_num, len(images)))


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    copy_coco_images(json_dict, args.images_folder, args.copy_to_folder, args.make_links, args.copy_ok)

