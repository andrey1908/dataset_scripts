import argparse
import json
import numpy as np
from copy import deepcopy
from shutil import copyfile
import os
from tqdm import tqdm


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-jsons', '--json-files', required=True, type=str, nargs='+')
    parser.add_argument('-img-flds', '--images-folders', required=True, type=str, nargs='+')
    parser.add_argument('-out', '--out-file', required=True, type=str)
    parser.add_argument('-out-img-fld', '--out-images-folder', required=True, type=str)
    return parser


def unite_categories(categories_list):
    new_categories = list()
    new_categories_names = list()
    category_name_to_new_id = dict()
    cat_id = 1
    for categories in categories_list:
        for category in categories:
            cat_name = category['name']
            if cat_name not in new_categories_names:
                new_categories_names.append(cat_name)
                new_categories.append({'supercategory': 'none', 'id': cat_id, 'name': cat_name})
                category_name_to_new_id[cat_name] = cat_id
                cat_id += 1

    old_category_id_to_new = list()
    for categories in categories_list:
        old_category_id_to_new_for_one = dict()
        for category in categories:
            old_category_id_to_new_for_one[category['id']] = category_name_to_new_id[category['name']]
        old_category_id_to_new.append(old_category_id_to_new_for_one)
    return new_categories, old_category_id_to_new


def unite_images(images_list, images_folders, out_images_folder):
    new_images = list()
    # woe means without extension
    used_images_names_woe = set()
    old_image_id_to_new = list()
    image_id = 0
    for i, images in tqdm(list(enumerate(images_list))):
        old_image_id_to_new_for_one = dict()
        for image in tqdm(images):
            image_name = image['file_name']
            # woe means without extension
            image_name_woe, extension = os.path.splitext(os.path.basename(image_name))
            new_image_name_woe = image_name_woe
            number_to_add = 1
            while new_image_name_woe in used_images_names_woe:
                new_image_name_woe = image_name_woe + '_{}'.format(number_to_add)
                number_to_add += 1
            used_images_names_woe.add(new_image_name_woe)
            new_image_name = new_image_name_woe + extension
            new_image = deepcopy(image)
            new_image.update({'file_name': new_image_name, 'id': image_id})
            new_images.append(new_image)
            old_image_id_to_new_for_one[image['id']] = image_id
            image_id += 1
            copyfile(os.path.join(images_folders[i], image_name), os.path.join(out_images_folder, new_image_name))
        old_image_id_to_new.append(old_image_id_to_new_for_one)  
    return new_images, old_image_id_to_new


def unite_annotations(annotations_list, old_image_id_to_new, old_category_id_to_new):
    new_annotations = list()
    ann_id = 1
    for i, annotations in enumerate(annotations_list):
        for annotation in annotations:
            new_annotation = deepcopy(annotation)
            old_image_id = annotation['image_id']
            old_category_id = annotation['category_id']
            new_image_id = old_image_id_to_new[i][old_image_id]
            new_category_id = old_category_id_to_new[i][old_category_id]
            new_annotation.update({'id': ann_id, 'image_id': new_image_id, 'category_id': new_category_id})
            new_annotations.append(new_annotation)
            ann_id += 1
    return new_annotations


def unite_datasets(json_dicts, images_folders, out_file, out_images_folder):
    assert(len(json_dicts) == len(images_folders))
    new_categories, old_category_id_to_new = unite_categories([json_dict['categories'] for json_dict in json_dicts])
    new_images, old_image_id_to_new = unite_images([json_dict['images'] for json_dict in json_dicts], images_folders, out_images_folder)
    new_annotations = unite_annotations([json_dict['annotations'] for json_dict in json_dicts], old_image_id_to_new, old_category_id_to_new)
    json_dict = {'images': new_images, 'annotations': new_annotations, 'categories': new_categories}
    with open(out_file, 'w') as f:
        json.dump(json_dict, f, indent=2)
    return json_dict


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    json_dicts = list()
    for json_file in args.json_files:
        with open(json_file, 'r') as f:
            json_dict = json.load(f)
            json_dicts.append(json_dict)
    unite_datasets(json_dicts, args.images_folders, args.out_file, args.out_images_folder)

