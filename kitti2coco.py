import argparse
import os
import json
from PIL import Image
import numpy as np


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-kitti-fld', '--kitti-folder', required=True, type=str, help='where kitti dataset is')
    parser.add_argument('-out', '--out-file', required=True, type=str)
    parser.add_argument('-split', '--split-rate', type=float, default=1, help='percentage (from 0 to 1)'
                                                                             ' of training images')
    parser.add_argument('-val-out', '--val-out-file', type=str)
    return parser


def get_images(images_folder, split_rate=None, start_id=0):
    train_images = list()
    val_images = list()
    image_files = os.listdir(images_folder)
    np.random.shuffle(image_files)
    num = len(image_files)
    train_num = int(num * split_rate)
    image_name_to_id = dict()

    idx = start_id
    for image_file in image_files[:train_num]:
        im = Image.open(os.path.join(images_folder, image_file))
        width, height = im.size
        image = {'file_name': image_file, 'width': width, 'height': height, 'id': idx}
        train_images.append(image)
        image_name_to_id[image_file] = idx
        idx += 1

    idx = start_id
    for image_file in image_files[train_num:]:
        im = Image.open(os.path.join(images_folder, image_file))
        width, height = im.size
        image = {'file_name': image_file, 'width': width, 'height': height, 'id': idx}
        val_images.append(image)
        image_name_to_id[image_file] = idx
        idx += 1

    return train_images, val_images, image_name_to_id


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


def get_annotations(annotations_folder, train_images, val_images, image_name_to_id, category_name_to_id, start_id=0):
    train_annotations = list()
    val_annotations = list()

    idx = start_id
    for train_image in train_images:
        image_path = train_image['file_name']
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
            train_annotations.append(annotation)
            idx += 1

    idx = start_id
    for val_image in val_images:
        image_path = val_image['file_name']
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
            bbox = [xtl, ytl, xbr - xtl, ybr - ytl]
            area = bbox[2] * bbox[3]
            image_id = image_name_to_id[image_name]
            annotation = {'area': area, 'iscrowd': 0, 'bbox': bbox, 'id': idx, 'image_id': image_id,
                          'category_id': category_id}
            val_annotations.append(annotation)
            idx += 1

    return train_annotations, val_annotations


def save_annotations(out_file, images, annotations, categories):
    json_dict = {'images': images, 'annotations': annotations, 'categories': categories}
    with open(out_file, 'w') as f:
        json.dump(json_dict, f)


def kitti2coco(kitti_folder, out_file, split_rate=1., val_out_file=None):
    assert 0 <= split_rate <= 1
    train_images, val_images, image_name_to_id = get_images(os.path.join(kitti_folder, 'image_2'), split_rate)
    categories, category_name_to_id = get_categories(os.path.join(kitti_folder, 'label_2'))
    train_annotations, val_annotations = get_annotations(os.path.join(kitti_folder, 'label_2'), train_images,
                                                         val_images, image_name_to_id, category_name_to_id)
    save_annotations(out_file, train_images, train_annotations, categories)
    if val_out_file is not None:
        save_annotations(val_out_file, val_images, val_annotations, categories)


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    kitti2coco(**vars(args))
