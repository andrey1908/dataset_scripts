import ctypes
import argparse
import json
import os
from utils.coco_tools import get_image_id_to_annotations_idxs, retain_annotations


class Box(ctypes.Structure):
    _fields_ = [('x', ctypes.c_float),
                ('y', ctypes.c_float),
                ('w', ctypes.c_float),
                ('h', ctypes.c_float),
                ('score', ctypes.c_float),
                ('idx', ctypes.c_int)]


nms_lib = ctypes.cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), 'nms.so'))
nms_lib.do_nms.restype = None
nms_lib.do_nms.argtypes = [ctypes.POINTER(Box), ctypes.c_int, ctypes.c_float]


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-thr', '--threshold', required=True, type=float)
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def coco_nms(json_dict, threshold):
    image_id_to_annotations_idxs = get_image_id_to_annotations_idxs(json_dict)
    idxs_to_leave = list()
    for image in json_dict['images']:
        boxes = list()
        annotations_idxs = image_id_to_annotations_idxs[image['id']]
        for ann_idx in annotations_idxs:
            ann = json_dict['annotations'][ann_idx]
            x, y, w, h = ann['bbox']
            box = Box()
            box.x, box.y, box.w, box.h = x + w/2, y + h/2, w, h
            box.score = ann['score']
            box.idx = ann_idx
            boxes.append(box)
        total = len(boxes)
        boxes = (Box*total)(*boxes)
        nms_lib.do_nms(boxes, total, threshold)
        for box in boxes:
            if box.score > 0:
                idxs_to_leave.append(box.idx)

    removed = len(json_dict['annotations']) - len(idxs_to_leave)
    retain_annotations(json_dict['annotations'], idxs_to_leave)
    return removed


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    removed = coco_nms(json_dict, args.threshold)
    print('Removed {} boxes'.format(removed))
    with open(args.out_file, 'w') as f:
        json.dump(json_dict, f, indent=2)

