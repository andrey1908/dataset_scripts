import argparse
import json
from pycocotools.mask import toBbox
from PIL import Image
import os


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ann', '--annotation-file', type=str, required=True)
    parser.add_argument('-img-fld', '--images-folder', type=str, required=True)
    parser.add_argument('-cls', '--classes', type=str, required=True, nargs='+')
    parser.add_argument('-out', '--out-file', type=str, required=True)
    return parser


def get_categories(classes):
    categories = list()
    cat_id = 1
    for cl in classes:
        cl_dict = {'name': cl, 'id': cat_id}
        categories.append(cl_dict)
        cat_id += 1
    return categories


def get_images(images_folder):
    images = list()
    images_files = os.listdir(images_folder)
    assert len(images_files[0].split('.')) == 2
    pad = len(images_files[0].split('.')[0])
    for image_file in images_files:
        assert len(image_file.split('.')) == 2
        assert len(image_file.split('.')[0]) == pad

    image_id = 0
    time_frame_to_image_id = dict()
    for image_file in images_files:
        im = Image.open(os.path.join(images_folder, image_file))
        width, height = im.size
        image = {'file_name': image_file, 'width': width, 'height': height, 'id': image_id}
        time_frame_to_image_id[int(image_file.split('.')[0])] = image_id
        images.append(image)
        image_id += 1
    return images, time_frame_to_image_id


def get_annotations(MOTS_lines, time_frame_to_image_id):
    annotations = list()
    ann_id = 1
    for MOTS_line in MOTS_lines:
        MOTS_line = MOTS_line.split()
        time_frame = int(MOTS_line[0])
        cat_id = int(MOTS_line[2])
        if cat_id not in [1, 2]:
            continue
        rleObj = {'counts': MOTS_line[5], 'size': [int(MOTS_line[3]), int(MOTS_line[4])]}
        bbox = list(toBbox(rleObj))
        annotation = dict()
        annotation['id'] = ann_id
        annotation["iscrowd"] = 0
        annotation["image_id"] = time_frame_to_image_id[time_frame]
        annotation["category_id"] = cat_id
        annotation["bbox"] = bbox
        annotation["area"] = bbox[2] * bbox[3]
        annotations.append(annotation)
        ann_id += 1
    return annotations


def MOTS_txt2coco_dict(MOTS_lines, images_folder, classes):
    images, time_frame_to_image_id = get_images(images_folder)
    categories = get_categories(classes)
    annotations = get_annotations(MOTS_lines, time_frame_to_image_id)
    json_dict = {'images': images, 'annotations': annotations, 'categories': categories}
    return json_dict


def MOTS2coco(annotation_file, images_folder, classes, out_file):
    with open(annotation_file, 'r') as f:
        MOTS_lines = f.read().splitlines()
    json_dict = MOTS_txt2coco_dict(MOTS_lines, images_folder, classes)
    with open(out_file, 'w') as f:
        json.dump(json_dict, f, indent=2)


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    MOTS2coco(**vars(args))
