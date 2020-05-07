import argparse
import json
from copy import deepcopy


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-jsons', '--json-files', required=True, type=str, nargs='+')
    parser.add_argument('-out', '--out-file', required=True, type=str)
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


def unite_images(images_list):
    new_images = list()
    new_images_names = set()
    new_images_data = set()
    image_name_to_new_id = dict()
    image_id = 0
    for images in images_list:
        for image in images:
            image_name = image['file_name']
            image_data = (image['file_name'], image['width'], image['height'])
            if image_name not in new_images_names:
                new_images_names.add(image_name)
                new_images_data.add(image_data)
                new_image = deepcopy(image)
                new_image.update({'id': image_id})
                new_images.append(new_image)
                image_name_to_new_id[image_name] = image_id
                image_id += 1
            elif image_data not in new_images_data:
                raise RuntimeError('Two images with same names and different parameters (except id)')

    old_image_id_to_new = list()
    for images in images_list:
        old_image_id_to_new_for_one = dict()
        for image in images:
            old_image_id_to_new_for_one[image['id']] = image_name_to_new_id[image['file_name']]
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


def unite_coco(json_dicts):
    new_categories, old_category_id_to_new = unite_categories([json_dict['categories'] for json_dict in json_dicts])
    new_images, old_image_id_to_new = unite_images([json_dict['images'] for json_dict in json_dicts])
    new_annotations = unite_annotations([json_dict['annotations'] for json_dict in json_dicts], old_image_id_to_new, old_category_id_to_new)
    json_dict = {'images': new_images, 'annotations': new_annotations, 'categories': new_categories}
    return json_dict


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    json_dicts = list()
    for json_file in args.json_files:
        with open(json_file, 'r') as f:
            json_dict = json.load(f)
            json_dicts.append(json_dict)
    json_dict = unite_coco(json_dicts)
    with open(args.out_file, 'w') as f:
        json.dump(json_dict, f, indent=2)

