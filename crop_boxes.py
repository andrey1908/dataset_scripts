import argparse
import json
import os
from PIL import Image
from tqdm import tqdm


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-img-fld', '--images-folder', required=True, type=str)
    parser.add_argument('-cls', '--classes', nargs='+', type=str)
    parser.add_argument('-out-fld', '--out-folder', required=True, type=str)
    parser.add_argument('-log', '--log-file', type=str)
    return parser


def get_image_id_to_annotations_idxs(images, annotations):
    image_id_to_annotations_idxs = dict()
    for i, ann in enumerate(annotations):
        annotations_idxs = image_id_to_annotations_idxs.get(ann['image_id'])
        if annotations_idxs is None:
            image_id_to_annotations_idxs[ann['image_id']] = [i]
        else:
            annotations_idxs.append(i)
    return image_id_to_annotations_idxs


def get_category_id_to_name(categories):
    category_id_to_name = dict()
    for category in categories:
        category_id_to_name[category['id']] = category['name']
    return category_id_to_name


def set_between(x, a, b):
    da = x - a
    db = x - b
    if da * db <= 0:
        return x
    if abs(da) < abs(db):
        return a
    else:
        return b


def preprocess_box(box, im_w, im_h):
    box[2] += box[0]
    box[3] += box[1]
    box[0] = set_between(box[0], 0, im_w)
    box[1] = set_between(box[1], 0, im_h)
    box[2] = set_between(box[2], 0, im_w)
    box[3] = set_between(box[3], 0, im_h)
    box[:] = [round(b) for b in box]


def crop_boxes(json_dict, images_folder, classes, out_folder):
    log = list()
    image_id_to_annotations_idxs = get_image_id_to_annotations_idxs(json_dict['images'], json_dict['annotations'])
    category_id_to_name = get_category_id_to_name(json_dict['categories'])
    boxes_counters = dict()
    fill_classes = False
    if classes == None:
        classes = list()
        fill_classes = True
    for category in json_dict['categories']:
        if fill_classes:
            boxes_counters[category['id']] = 1
            os.makedirs(os.path.join(out_folder, category['name']), exist_ok=True)
            classes.append(category['name'])
        elif category['name'] in classes:
            boxes_counters[category['id']] = 1
            os.makedirs(os.path.join(out_folder, category['name']), exist_ok=True)

    for image in tqdm(json_dict['images']):
        log_image = {'original_file_name': image['file_name'], 'crops': list()}
        im = Image.open(os.path.join(images_folder, image['file_name']))
        annotations_idxs = image_id_to_annotations_idxs[image['id']]
        for annotation_idx in annotations_idxs:
            ann = json_dict['annotations'][annotation_idx]
            cat_id = ann['category_id']
            cat_name = category_id_to_name[cat_id]
            if cat_name not in classes:
                continue
            box = list(ann['bbox'])
            preprocess_box(box, im.size[0], im.size[1])
            if (box[0] >= box[2]) or (box[1] >= box[3]):
                continue
            croped = im.crop(tuple(box))
            croped.save(os.path.join(out_folder, cat_name, '{}.png'.format(boxes_counters[cat_id])))
            log_crop = {'cropped_file_name': os.path.join(cat_name, '{}.png'.format(boxes_counters[cat_id])),
                        'box': box}  # xtl, ytl, xbr, ybr
            log_image['crops'].append(log_crop)
            boxes_counters[cat_id] += 1
        log.append(log_image)
    return log


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    log = crop_boxes(json_dict, args.images_folder, args.classes, args.out_folder)
    if args.log_file is not None:
        with open(args.log_file, 'w') as f:
            json.dump(log, f, indent = 2)

