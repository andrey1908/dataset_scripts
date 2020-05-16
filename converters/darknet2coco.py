import os
import argparse
from tqdm import tqdm
from PIL import Image
import json


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-img-list', '--images-list-file', required=True, type=str)
    parser.add_argument('-img-fld', '--images-folder', type=str, default='')
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def image_file2label_file(image_file):
    label_file = image_file.split('/')
    for i in range(len(label_file)):
        if label_file[i] == 'images':
            label_file[i] = 'labels'
    label_file = '/'.join(label_file)

    label_file = label_file.split('.')
    label_file[-1] = 'txt'
    label_file = '.'.join(label_file)
    return label_file


def darknet_list2coco_dict(images_list, images_folder):
    images = list()
    image_id = 0
    annotations = list()
    ann_id = 1
    max_cat_id = 0
    for image_file in tqdm(images_list):
        im = Image.open(os.path.join(images_folder, image_file))
        width, height = im.size
        image = {'id': image_id, 'file_name': image_file, 'width': width, 'height': height}
        images.append(image)
        label_file = image_file2label_file(os.path.join(images_folder, image_file))
        with open(label_file, 'r') as f:
            ann_lines = f.readlines()
        for ann_line in ann_lines:
            ann_line = ann_line.split(' ')
            cat_id = int(ann_line[0])
            max_cat_id = max(max_cat_id, cat_id)
            xtl = (float(ann_line[1]) - float(ann_line[3])/2)*width
            ytl = (float(ann_line[2]) - float(ann_line[4])/2)*height
            w = float(ann_line[3]) * width
            h = float(ann_line[4]) * height
            ann = {'id': ann_id, 'iscrowd': 0, 'image_id': image_id, 'category_id': cat_id+1, 'bbox': [xtl, ytl, w, h], 'area': w*h}
            annotations.append(ann)
            ann_id += 1
        image_id += 1

    categories = list()
    for cat_id in range(max_cat_id+1):
        cat = {'name': str(cat_id), 'id': cat_id+1}
        categories.append(cat)

    json_dict = {'images': images, 'annotations': annotations, 'categories': categories}
    return json_dict


def darknet2coco(images_list_file, out_file, images_folder=''):
    images_list = list()
    with open(args.images_list_file, 'r') as f:
        images_list = f.readlines()
    for i in range(len(images_list)):
        if images_list[i][-1] == '\n':
            images_list[i] = images_list[i][:-1]
    json_dict = darknet_list2coco_dict(images_list, args.images_folder)
    with open(out_file, 'w') as f:
        json.dump(json_dict, f, indent=2)


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    darknet2coco(**vars(args))

