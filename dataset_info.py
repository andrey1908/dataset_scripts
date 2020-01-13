import json
import argparse


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    return parser


def get_images_shapes(coco_file):
    with open(coco_file, 'r') as f:
        json_dict = json.load(f)
    images = json_dict['images']
    shapes = dict()
    w = 0
    h = 0
    for image in images:
        shape = (image['width'], image['height'])
        if shape not in shapes.keys():
            shapes[shape] = 0
        shapes[shape] += 1
        w += image['width']
        h += image['height']
    avr_w = w / len(images)
    avr_h = h / len(images)
    return shapes, (avr_w, avr_h)


def get_min_area(coco_file):
    with open(coco_file, 'r') as f:
        json_dict = json.load(f)
    annotations = json_dict['annotations']
    areas = list()
    for annotation in annotations:
        areas.append(annotation['area'])
    return min(areas)


def images_number(json_file):
    with open(json_file, 'r') as f:
        json_dict = json.load(f)
    return(len(json_dict['images']))


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    img_num = images_number(**vars(args))
    print(img_num)

