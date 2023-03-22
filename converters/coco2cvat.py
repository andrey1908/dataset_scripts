import xml.etree.ElementTree as xml
import json
import argparse
from xml.dom import minidom
from utils.coco_tools import get_image_id_to_annotations_idxs


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', type=str, required=True)
    parser.add_argument('-out', '--out-file', type=str, required=True)
    parser.add_argument('-reindex-images', '--reindex-images', action='store_true')
    return parser


def get_cvat_root_template(json_dict):
    annotations = xml.Element("annotations")
    meta = xml.SubElement(annotations, "meta")
    task = xml.SubElement(meta, "task")
    size = xml.SubElement(task, "size").text = str(len(json_dict['images']))
    mode = xml.SubElement(task, "mode").text = "annotation"
    overlap = xml.SubElement(task, "overlap").text = "0"
    flipped = xml.SubElement(task, "flipped").text = "False"
    labels = xml.SubElement(task, "labels")
    return annotations, labels


def fill_cvat_labels(cvat_labels, categories):
    category_id_to_name = dict()
    for category in categories:
        cvat_label = xml.SubElement(cvat_labels, "label")
        xml.SubElement(cvat_label, "name").text = category['name']
        category_id_to_name[category['id']] = category['name']
    return category_id_to_name


def get_images_order(images, reindex_images):
    if reindex_images:
        images_names = [image['file_name'] for image in images]
        images_order = list(zip(*sorted(zip(images_names, list(range(len(images)))))))[1]
    else:
        images_order = list(range(len(images)))
    return images_order


def coco_segmentation_to_cvat(coco_segmentation):
    cvat_segmentation = ''
    coco_segmentation = coco_segmentation[0]
    for i in range(len(coco_segmentation))[::2]:
        cvat_segmentation = cvat_segmentation + str(coco_segmentation[i]) + ',' + str(coco_segmentation[i+1]) + ';'
    cvat_segmentation = cvat_segmentation[:-1]
    return cvat_segmentation


def set_between(x, a, b):
    da = x - a
    db = x - b
    if da * db <= 0:
        return x
    if abs(da) < abs(db):
        return a
    else:
        return b


def coco_dict2cvat_root(json_dict, reindex_images=False):
    cvat_annotations, cvat_labels = get_cvat_root_template(json_dict)
    category_id_to_name = fill_cvat_labels(cvat_labels, json_dict['categories'])
    image_id_to_anns_idxs = get_image_id_to_annotations_idxs(json_dict)
    images_order = get_images_order(json_dict['images'], reindex_images)
    image_id = 0
    for i in images_order:
        json_image = json_dict['images'][i]
        xml_image = dict()
        xml_image['id'] = str(image_id)
        xml_image['name'] = json_image['file_name']
        xml_image['width'] = str(json_image['width'])
        xml_image['height'] = str(json_image['height'])
        cvat_image = xml.SubElement(cvat_annotations, "image", xml_image)
        image_id += 1
        for ann_idx in image_id_to_anns_idxs[json_image['id']]:
            json_ann = json_dict['annotations'][ann_idx]
            if 'segmentation' in json_ann.keys():
                xml_ann = dict()
                xml_ann['label'] = category_id_to_name[json_ann['category_id']]
                xml_ann['occluded'] = '0'
                xml_ann['points'] = coco_segmentation_to_cvat(json_ann['segmentation'])
                if 'score' in json_ann.keys():
                    xml_ann['score'] = str(json_ann['score'])
                xml.SubElement(cvat_image, 'polygon', xml_ann)
            else:
                xml_ann = dict()
                xml_ann['label'] = category_id_to_name[json_ann['category_id']]
                xml_ann['occluded'] = '0'
                xml_ann['xtl'] = str(set_between(json_ann['bbox'][0], 0, json_image['width']))
                xml_ann['ytl'] = str(set_between(json_ann['bbox'][1], 0, json_image['height']))
                xml_ann['xbr'] = str(set_between(json_ann['bbox'][0] + json_ann['bbox'][2], 0, json_image['width']))
                xml_ann['ybr'] = str(set_between(json_ann['bbox'][1] + json_ann['bbox'][3], 0, json_image['height']))
                if 'score' in json_ann.keys():
                    xml_ann['score'] = str(json_ann['score'])
                xml.SubElement(cvat_image, 'box', xml_ann)
    return cvat_annotations


def coco2cvat(json_file, out_file, reindex_images=False):
    with open(json_file, 'r') as f:
        json_dict = json.load(f)
    cvat_root = coco_dict2cvat_root(json_dict, reindex_images)
    rough_string = xml.tostring(cvat_root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    with open(out_file, "w") as f:
        f.writelines(reparsed.toprettyxml(indent='  '))


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    coco2cvat(**vars(args))

