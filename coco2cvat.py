import xml.etree.ElementTree as xml
import json
import argparse
from xml.dom import minidom


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', type=str, required=True)
    parser.add_argument('-out', '--out-file', type=str, required=True)
    parser.add_argument('-reindex-images', '--reindex-images', action='store_true')
    return parser


def coco_segmentation_to_cvat(coco_segmentation):
    cvat_segmentation = ''
    coco_segmentation = coco_segmentation[0]
    for i in range(len(coco_segmentation))[::2]:
        cvat_segmentation = cvat_segmentation + str(coco_segmentation[i]) + ',' + str(coco_segmentation[i+1]) + ';'
    cvat_segmentation = cvat_segmentation[:-1]
    return cvat_segmentation


def coco_dict_to_cvat_root(json_dict, reindex_images=False):
    annotations = xml.Element("annotations")
    meta = xml.SubElement(annotations, "meta")
    task = xml.SubElement(meta, "task")
    size = xml.SubElement(task, "size").text = str(len(json_dict['images']))
    mode = xml.SubElement(task, "mode").text = "annotation"
    overlap = xml.SubElement(task, "overlap").text = "0"
    flipped = xml.SubElement(task, "flipped").text = "False"
    labels = xml.SubElement(task, "labels")

    category_id_to_name = dict()
    for category in json_dict['categories']:
        label = xml.SubElement(labels, "label")
        name = xml.SubElement(label, "name").text = category['name']
        category_id_to_name[category['id']] = category['name']

    image_id_to_anns_idxs = dict()
    for json_image in json_dict['images']:
        image_id_to_anns_idxs[json_image['id']] = list()
    for i in range(len(json_dict['annotations'])):
        image_id = json_dict['annotations'][i]['image_id']
        image_id_to_anns_idxs[image_id].append(i)
    if reindex_images:
        json_dict['images'] = list(zip(*sorted(zip([json_dict['images'][i]['file_name'] for i in range(len(json_dict['images']))], json_dict['images']))))[1]
        image_id = 0
    for json_image in json_dict['images']:
        xml_image = dict()
        if reindex_images:
            xml_image['id'] = str(image_id)
            image_id += 1
        else:
            xml_image['id'] = str(json_image['id'])
        xml_image['name'] = json_image['file_name']
        xml_image['width'] = str(json_image['width'])
        xml_image['height'] = str(json_image['height'])
        img = xml.SubElement(annotations, "image", xml_image)
        for ann_idx in image_id_to_anns_idxs[json_image['id']]:
            json_ann = json_dict['annotations'][ann_idx]
            if 'segmentation' in json_ann.keys():
                xml_ann = dict()
                xml_ann['label'] = category_id_to_name[json_ann['category_id']]
                xml_ann['occluded'] = '0'
                xml_ann['points'] = coco_segmentation_to_cvat(json_ann['segmentation'])
                if 'score' in json_ann.keys():
                    xml_ann['score'] = str(json_ann['score'])
                xml.SubElement(img, 'polygon', xml_ann)
            else:
                xml_ann = dict()
                xml_ann['label'] = category_id_to_name[json_ann['category_id']]
                xml_ann['occluded'] = '0'
                xml_ann['xtl'] = str(json_ann['bbox'][0])
                xml_ann['ytl'] = str(json_ann['bbox'][1])
                xml_ann['xbr'] = str(json_ann['bbox'][0] + json_ann['bbox'][2])
                xml_ann['ybr'] = str(json_ann['bbox'][1] + json_ann['bbox'][3])
                if 'score' in json_ann.keys():
                    xml_ann['score'] = str(json_ann['score'])
                xml.SubElement(img, 'box', xml_ann)
    return annotations


def coco2cvat(json_file, out_file, reindex_images=False):
    with open(json_file, 'r') as f:
        json_dict = json.load(f)
    root = coco_dict_to_cvat_root(json_dict, reindex_images)
    rough_string = xml.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    with open(out_file, "w") as f:
        f.writelines(reparsed.toprettyxml(indent='  '))


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    coco2cvat(**vars(args))
