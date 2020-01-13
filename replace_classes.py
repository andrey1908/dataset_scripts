import argparse
import json
from reindex_json import reindex_json


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def replace_categories(categories):
    new_categories = [{"supercategory": "none", "id": 1, "name": "traffic_sign"},
                      {"supercategory": "none", "id": 2, "name": "car"},
                      {"supercategory": "none", "id": 3, "name": "person"},
                      {"supercategory": "none", "id": 4, "name": "traffic_light"}]
    old_category_name_to_new_id = {'1.22': 1, '1.23': 1, '2.4': 1, '2.5': 1, '3.1': 1, '3.2': 1, '3.24': 1, '3.4': 1, '5.19': 1, '3.25+3.31': 1, 'car': 2, 'other': 1, 'person': 3, 'stop_sign': 1, 'traffic_light': 4, 'truck': 2}
    old_category_id_to_new = dict()
    for old_category in categories:
        if old_category['name'] in old_category_name_to_new_id.keys():
            old_category_id_to_new[old_category['id']] = old_category_name_to_new_id[old_category['name']]
    categories[:] = new_categories
    return old_category_id_to_new


def correct_annotations(annotations, old_category_id_to_new):
    for i in range(len(annotations)-1,-1,-1):
        if annotations[i]['category_id'] not in old_category_id_to_new.keys():
            del annotations[i]
            continue
        annotations[i]['category_id'] = old_category_id_to_new[annotations[i]['category_id']]


def replace_classes(json_dict):
    old_category_id_to_new = replace_categories(json_dict['categories'])
    correct_annotations(json_dict['annotations'], old_category_id_to_new)
    reindex_json(json_dict)


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    replace_classes(json_dict)
    with open(args.out_file, 'w') as f:
        json.dump(json_dict, f, indent=2)

