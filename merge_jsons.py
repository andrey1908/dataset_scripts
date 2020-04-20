import argparse
import json
from mmdet.ops.nms import nms
import numpy as np


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-dets', '--detections-file', required=True, type=str)
    parser.add_argument('-info', '--info-file', required=True, type=str)
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.detections_file, 'r') as f:
        detections = json.load(f)
    with open(args.info_file, 'r') as f:
        info = json.load(f)
    json_dict = {'images': info['images'], 'annotations': detections, 'categories': info['categories']}
    with open(args.out_file, 'w') as f:
        json.dump(json_dict, f, indent=2)

