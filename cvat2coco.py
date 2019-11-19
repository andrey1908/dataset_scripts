import os
import xml.etree.ElementTree as xml
import json
import argparse
import re


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-xml', '--xml-file', type=str, required=True)
    parser.add_argument('-out', '--out-file', type=str, required=True)
    parser.add_argument('-det_only', '--detections-only', action='store_true')
    return parser


def cvat_segmentation_to_coco(cvat_segmentation):
    coco_segmentation = [float(x) for x in re.split(',|;', cvat_segmentation)]
    return coco_segmentation


def segmentation_to_bbox(segmentation):
    x = segmentation[0::2]
    y = segmentation[1::2]
    bbox = [min(x), min(y), max(x)-min(x), max(y)-min(y)]
    return bbox


def cvat_root_to_coco_dict(root):
    images = []
    annotations = []
    categories = []

    # get categories
    labels = root.find('meta').find('task').find('labels')
    class_to_idx = {}
    idx = 1
    for label in labels:
        category = {"id": idx, "name": label[0].text}
        categories.append(category)
        class_to_idx[label.find('name').text] = idx
        idx += 1

    # get images and annotations
    idx = 1
    for image in root.findall('image'):
        image.attrib["id"] = int(image.attrib["id"])
        image.attrib["height"] = int(image.attrib["height"])
        image.attrib["width"] = int(image.attrib["width"])
        image.attrib["file_name"] = image.attrib.pop("name")
        images.append(image.attrib)
        for box in image.findall('box'):
            annotation = dict()
            bbox = [float(box.attrib["xtl"]), float(box.attrib["ytl"]),
                    float(box.attrib["xbr"]) - float(box.attrib["xtl"]),
                    float(box.attrib["ybr"]) - float(box.attrib["ytl"])]
            annotation["area"] = bbox[2] * bbox[3]
            annotation["iscrowd"] = 0
            annotation["image_id"] = int(image.attrib["id"])
            annotation["bbox"] = bbox
            annotation["category_id"] = class_to_idx[box.attrib["label"]]
            annotation["id"] = idx
            if "score" in box.attrib.keys():
                annotation["score"] = float(box.attrib["score"])
            annotations.append(annotation)
            idx += 1
        for polygon in image.findall('polygon'):
            annotation = dict()
            annotation["iscrowd"] = 0
            annotation["image_id"] = int(image.attrib["id"])
            annotation["segmentation"] = cvat_segmentation_to_coco(polygon.attrib["points"])
            annotation["bbox"] = segmentation_to_bbox(annotation["segmentation"])
            annotation["area"] = annotation["bbox"][2] * annotation["bbox"][3]
            annotation["category_id"] = class_to_idx[polygon.attrib["label"]]
            annotation["id"] = idx
            if "score" in polygon.attrib.keys():
                annotation["score"] = float(polygon.attrib["score"])
            annotations.append(annotation)
            idx += 1

    json_dict = {'images': images, 'annotations': annotations, 'categories': categories}
    return json_dict


def cvat2coco(xml_file, out_file, detections_only=False):
    tree = xml.parse(xml_file)
    root = tree.getroot()
    json_dict = cvat_root_to_coco_dict(root)
    if detections_only:
        json_dict = json_dict['annotations']
    with open(out_file, 'w') as f:
        json.dump(json_dict, f, indent=2)


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    cvat2coco(**vars(args))
