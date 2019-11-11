import json
import os
from tqdm import tqdm
import argparse


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-root-fld', '--root-folder', required=True, type=str)
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def coco2keras_yolo(json_file, root_folder, out_file):
    with open(json_file, 'r') as f:
        json_dict = json.load(f)
    images = json_dict['images']
    annotations = json_dict['annotations']

    out = []
    for i, image in tqdm(enumerate(images)):
        line = ''
        line = line + os.path.join(root_folder, image['file_name']) + ' '
        for annotation in annotations:
            if annotation['image_id'] == image['id']:
                xtl = annotation['bbox'][0]
                ytl = annotation['bbox'][1]
                xbr = annotation['bbox'][0] + annotation['bbox'][2]
                ybr = annotation['bbox'][1] + annotation['bbox'][3]
                category = annotation['category_id'] - 1
                line = line + ','.join([str(int(xtl)), str(int(ytl)), str(int(xbr)), str(int(ybr)), str(category)]) +\
                       ' '
        line = line + '\n'
        out.append(line)

    with open(out_file, 'w') as f:
        f.writelines(out)


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    kwargs = vars(args)
    coco2keras_yolo(**kwargs)
