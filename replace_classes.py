import argparse
import json


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-coco', '--coco-file', required=True, type=str)
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def get_new_categories(old_categories):
    new_categories = [{"supercategory": "none", "id": 1, "name": "traffic_sign"},
                      {"supercategory": "none", "id": 2, "name": "car"},
                      {"supercategory": "none", "id": 3, "name": "truck"},
                      {"supercategory": "none", "id": 4, "name": "person"},
                      {"supercategory": "none", "id": 5, "name": "traffic_light"}]
    old_category_name_to_new_id = {'1.22': 1, '1.23': 1, '2.4': 1, '2.5': 1, '3.1': 1, '3.2': 1, '3.24': 1, '3.4': 1, '5.19': 1, 'other': 1, 'stop_sign': 1, 'car': 2, 'truck': 3, 'person': 4, 'traffic_light': 5}
    old_category_id_to_new = dict()
    for old_category in old_categories:
        if old_category['name'] in old_category_name_to_new_id.keys():
            old_category_id_to_new[old_category['id']] = old_category_name_to_new_id[old_category['name']]
    return new_categories, old_category_id_to_new


def get_new_annotations(annotations, old_category_id_to_new, start_id=1):
    new_annotations = list()
    used_images_id = set()
    idx = start_id
    for annotation in annotations:
        if annotation['category_id'] not in old_category_id_to_new.keys():
            continue
        annotation['category_id'] = old_category_id_to_new[annotation['category_id']]
        annotation['id'] = idx
        new_annotations.append(annotation)
        used_images_id.add(annotation['image_id'])
        idx += 1
    return new_annotations, used_images_id


def get_new_images(images, used_images_id, start_id=0):
    new_images = list()
    old_image_id_to_new = dict()
    idx = start_id
    for image in images:
        if image['id'] not in used_images_id:
            # continue
            pass
        old_image_id_to_new[image['id']] = idx
        image['id'] = idx
        new_images.append(image)
        idx += 1
    return new_images, old_image_id_to_new


def correct_annotations(coco_file, out_file):
    with open(coco_file, 'r') as f:
        json_dict = json.load(f)
    images = json_dict['images']
    annotations = json_dict['annotations']
    categories = json_dict['categories']

    categories, old_category_id_to_new = get_new_categories(categories)
    annotations, used_images_id = get_new_annotations(annotations, old_category_id_to_new)
    images, old_image_id_to_new = get_new_images(images, used_images_id)
    for annotation in annotations:
        annotation['image_id'] = old_image_id_to_new[annotation['image_id']]

    json_dict = {'images': images, 'annotations': annotations, 'categories': categories}
    with open(out_file, 'w') as f:
        json.dump(json_dict, f)


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    correct_annotations(**vars(args))
