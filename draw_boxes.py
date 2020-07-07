import argparse
import json
import os
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
from pathlib import Path
import numpy as np
from utils import UniquePathsNamesGenerator
from utils.coco_tools import get_image_id_to_annotations, get_category_id_to_name, find_image_by_name
from numpy import clip


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-img-fld', '--images-folder', required=True, type=str)
    parser.add_argument('-out-fld', '--out-folder', required=True, type=str)
    parser.add_argument('-imgs-to-draw', '--images-files-to-draw', type=str, nargs='+')
    parser.add_argument('-num', '--images-number', type=int)
    parser.add_argument('-rnd', '--random', action='store_true')
    parser.add_argument('-owb', '--only-with-boxes', action='store_true')
    parser.add_argument('-img-json', '--images-json-file', type=str)
    parser.add_argument('-preserve-files-tree', '--preserve-files-tree', action='store_true')
    parser.add_argument('-thr', '--threshold', type=float, default=0.)
    return parser


def preprocess_box(box, im_w, im_h):
    box[2] += box[0]
    box[3] += box[1]
    box[0] = clip(box[0], 0, im_w)
    box[1] = clip(box[1], 0, im_h)
    box[2] = clip(box[2], 0, im_w)
    box[3] = clip(box[3], 0, im_h)
    box[:] = [round(b) for b in box]


def get_images_idxs_with_boxes(json_dict, threshold=0.):
    image_id_to_idx = dict()
    for i, image in enumerate(json_dict['images']):
        image_id_to_idx[image['id']] = i
    images_idxs_with_boxes = set()
    for ann in json_dict['annotations']:
        if ann.get('score', 999.) >= threshold:
            images_idxs_with_boxes.add(image_id_to_idx[ann['image_id']])
    return list(images_idxs_with_boxes)


def get_images_to_draw(json_dict, images_folder, images_files_to_draw=None, images_number=None, random=False, only_with_boxes=False,
                       threshold=0.):
    images = json_dict['images']
    if images_files_to_draw:
        images_to_draw = list()
        for image_file_to_draw in images_files_to_draw:
            image_name = os.path.relpath(image_file_to_draw, images_folder)
            images_to_draw.append(find_image_by_name(json_dict, image_name))
    elif images_number:
        if only_with_boxes:
            images_idxs = get_images_idxs_with_boxes(json_dict, threshold)
        else:
            images_idxs = list(range(len(images)))
        if images_number > len(images_idxs):
            raise RuntimeError('There aren\'t so many images to draw. Maximum {} images.'.format(len(images_idxs)))
        if random:
            np.random.shuffle(images_idxs)
        images_to_draw = list()
        for i in range(images_number):
            images_to_draw.append(images[images_idxs[i]])
    else:
        images_to_draw = images
    return images_to_draw


def draw_boxes(json_dict, images_folder, out_folder, images_files_to_draw=None, images_number=None, random=False,
               only_with_boxes=False, preserve_files_tree=False, threshold=0.):
    Path(out_folder).mkdir(parents=True, exist_ok=True)
    image_id_to_annotations = get_image_id_to_annotations(json_dict)
    category_id_to_name = get_category_id_to_name(json_dict)
    images_to_draw = get_images_to_draw(json_dict, images_folder, images_files_to_draw, images_number, random, only_with_boxes,
                                        threshold)
    if images_to_draw is None:
        raise RuntimeError()
    uniquer = UniquePathsNamesGenerator()
    for image in tqdm(images_to_draw):
        im = Image.open(os.path.join(images_folder, image['file_name']))
        annotations = image_id_to_annotations[image['id']]
        for ann in annotations:
            score_str = ''
            if 'score' in ann.keys():
                score_str = ' ' + str(ann['score'])[:4]
                if ann['score'] < threshold:
                    continue
            cat_id = ann['category_id']
            cat_name = category_id_to_name[cat_id]
            box = list(ann['bbox'])
            preprocess_box(box, im.size[0], im.size[1])
            if (box[0] >= box[2]) or (box[1] >= box[3]):
                continue
            im_draw = ImageDraw.Draw(im)
            width = int(max(im.size)/1300) + 1
            im_draw.rectangle(box, outline='red', width=width)
            font_size = int(max(im.size)/100) + 10
            font = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', font_size)
            text_x = min(box[0], im.width-font.getsize(cat_name + score_str)[0])
            text_y = max(box[1]-font_size, 0)
            im_draw.text((text_x, text_y), cat_name + score_str, fill='red', font=font)
        rel_out_image_path = image['file_name'] if preserve_files_tree else os.path.basename(image['file_name'])
        out_image_path = os.path.join(out_folder, rel_out_image_path)
        out_image_path = uniquer.unique(out_image_path)
        if preserve_files_tree:
            Path(os.path.dirname(out_image_path)).mkdir(parents=True, exist_ok=True)
        im.save(out_image_path)


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    if args.images_json_file:
        with open(args.images_json_file, 'r') as f:
            images = json.load(f)
            json_dict = {'images': images['images'], 'annotations': json_dict, 'categories': images['categories']}
    draw_boxes(json_dict, args.images_folder, args.out_folder,
               images_files_to_draw=args.images_files_to_draw, images_number=args.images_number, random=args.random,
               only_with_boxes=args.only_with_boxes, preserve_files_tree=args.preserve_files_tree, threshold=args.threshold)

