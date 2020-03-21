import argparse
import os
import json
from PIL import Image
import numpy as np


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-kitti-fld', '--kitti-folder', required=True, type=str, help='where kitti dataset is')
    parser.add_argument('-out', '--out-file', required=True, type=str, help='where to save converted'
                                                                                          ' annotation file')
    return parser


def get_images(images_folder, start_id=0):
    images = list()
    image_files = os.listdir(images_folder)
    sorted(image_files)
    num = len(image_files)
    image_name_to_id = dict()

    idx = start_id
    for image_file in image_files:
        im = Image.open(os.path.join(images_folder, image_file))
        width, height = im.size
        image = {'file_name': image_file, 'width': width, 'height': height, 'id': idx}
        images.append(image)
        image_name_to_id[image_file] = idx
        idx += 1
    return images, image_name_to_id


def get_categories(annotations_folder, start_id=1):
    categories = list()
    annotation_files = os.listdir(annotations_folder)
    category_name_to_id = dict()
    idx = start_id
    for annotation_file in annotation_files:
        with open(os.path.join(annotations_folder, annotation_file), 'r') as f:
            lines = f.readlines()
        for line in lines:
            category_name = line.split(' ')[0]
            if (category_name not in category_name_to_id.keys()) and (category_name != 'DontCare'):
                category = {'name': category_name, 'id': idx}
                categories.append(category)
                category_name_to_id[category_name] = idx
                idx += 1
    return categories, category_name_to_id


def get_annotations(annotations_folder, images, image_name_to_id, category_name_to_id, start_id=0):
    annotations = list()
    idx = start_id
    for image in images:
        image_path = image['file_name']
        image_name = image_path.split('/')[-1]
        annotation_file = image_name[:-3] + 'txt'
        with open(os.path.join(annotations_folder, annotation_file), 'r') as f:
            lines = f.readlines()
        for line in lines:
            bbox_info = line.split(' ')
            category_name = bbox_info[0]
            if category_name == 'DontCare':
                continue
            category_id = category_name_to_id[category_name]
            xtl, ytl, xbr, ybr = float(bbox_info[4]), float(bbox_info[5]), float(bbox_info[6]), float(bbox_info[7])
            bbox = [xtl, ytl, xbr-xtl, ybr-ytl]
            area = bbox[2] * bbox[3]
            image_id = image_name_to_id[image_name]
            annotation = {'area': area, 'iscrowd': 0, 'bbox': bbox, 'id': idx, 'image_id': image_id,
                          'category_id': category_id}
            annotations.append(annotation)
            idx += 1
    return annotations


def kitti2coco(kitti_folder):
    images, image_name_to_id = get_images(os.path.join(kitti_folder, 'image_2'))
    categories, category_name_to_id = get_categories(os.path.join(kitti_folder, 'label_2'))
    annotations = get_annotations(os.path.join(kitti_folder, 'label_2'), images, image_name_to_id, category_name_to_id)
    json_dict = {'images': images, 'annotations': annotations, 'categories': categories}
    return json_dict


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    json_dict = kitti2coco(args.kitti_folder)
    with open(args.out_file, 'w') as f:
        json.dump(json_dict, f, indent=2)

