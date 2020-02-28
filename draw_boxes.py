import argparse
import json
import os
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-img-fld', '--images-folder', required=True, type=str)
    parser.add_argument('-out-fld', '--out-folder', required=True, type=str)
    parser.add_argument('-num', '--images-number', type=int)
    return parser


def get_image_id_to_annotations_idxs(images, annotations):
    image_id_to_annotations_idxs = dict()
    for image in images:
        image_id_to_annotations_idxs[image['id']] = list()
    for i, ann in enumerate(annotations):
        image_id_to_annotations_idxs[ann['image_id']].append(i)
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


def draw_boxes(json_dict, images_folder, out_folder, images_number=None, font_size=20):
    image_id_to_annotations_idxs = get_image_id_to_annotations_idxs(json_dict['images'], json_dict['annotations'])
    category_id_to_name = get_category_id_to_name(json_dict['categories'])
    if images_number is None:
        images_number = len(json_dict['images'])
    for image in tqdm(json_dict['images'][:images_number]):
        im = Image.open(os.path.join(images_folder, image['file_name']))
        annotations_idxs = image_id_to_annotations_idxs[image['id']]
        for annotation_idx in annotations_idxs:
            ann = json_dict['annotations'][annotation_idx]
            cat_id = ann['category_id']
            cat_name = category_id_to_name[cat_id]
            box = list(ann['bbox'])
            preprocess_box(box, im.size[0], im.size[1])
            if (box[0] >= box[2]) or (box[1] >= box[3]):
                continue
            im_draw = ImageDraw.Draw(im)   
            im_draw.rectangle(box, outline='red')
            font = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', font_size)
            im_draw.text((box[0], box[1]-font_size), cat_name, fill='red', font=font)
        im.save(os.path.join(out_folder, image['file_name'].split('/')[-1]))


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    draw_boxes(json_dict, args.images_folder, args.out_folder, args.images_number)

