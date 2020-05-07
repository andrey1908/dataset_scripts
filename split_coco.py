import argparse
import json
import numpy as np
from copy import deepcopy
from reindex_coco import reindex_coco


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-train', '--train-out-file', required=True, type=str)
    parser.add_argument('-test', '--test-out-file', required=True, type=str)
    parser.add_argument('-sr', '--split-rate', type=float, default=0.8, help='Percentage of training images.')
    return parser


def get_image_id_to_annotations_idxs(json_dict):
    image_id_to_annotations_idxs = dict()
    for image in json_dict['images']:
        image_id_to_annotations_idxs[image['id']] = list()
    for i, annotation in enumerate(json_dict['annotations']):
        image_id = annotation['image_id']
        image_id_to_annotations_idxs[image_id].append(i)
    return image_id_to_annotations_idxs


def split_coco_dict(json_dict, split_rate):
    images = deepcopy(json_dict['images'])
    np.random.shuffle(images)
    train_images = images[:int(len(images)*split_rate)]
    test_images = images[int(len(images)*split_rate):]
    del images
    
    image_id_to_annotations_idxs = get_image_id_to_annotations_idxs(json_dict)

    train_annotations = list()
    test_annotations = list()
    for train_image in train_images:
        for i in image_id_to_annotations_idxs[train_image['id']]:
            annotation = deepcopy(json_dict['annotations'][i])
            train_annotations.append(annotation)
    for test_image in test_images:
        for i in image_id_to_annotations_idxs[test_image['id']]:
            annotation = deepcopy(json_dict['annotations'][i])
            test_annotations.append(annotation)

    train_json_dict = {'images': train_images, 'annotations': train_annotations, 'categories': deepcopy(json_dict['categories'])}
    test_json_dict = {'images': test_images, 'annotations': test_annotations, 'categories': deepcopy(json_dict['categories'])}
    reindex_coco(train_json_dict)
    reindex_coco(test_json_dict)
    return train_json_dict, test_json_dict


def split_coco(json_file, train_out_file, test_out_file, split_rate):
    with open(json_file, 'r') as f:
        json_dict = json.load(f)
    train_json_dict, test_json_dict = split_coco_dict(json_dict, split_rate)
    with open(train_out_file, 'w') as f:
        json.dump(train_json_dict, f, indent=2)
    with open(test_out_file, 'w') as f:
        json.dump(test_json_dict, f, indent=2)


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    split_coco(**vars(args))
