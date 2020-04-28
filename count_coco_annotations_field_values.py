import argparse
import json


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-f', '--field', required=True, type=str)
    return parser


def count_coco_annotations_field_values(annotations, field):
    field_values_num = dict()
    field_values_num['without that field'] = 0
    for ann in annotations:
        value = ann.get(field)
        if value is None:
            field_values_num['without that field'] += 1
        if value not in field_values_num.keys():
            field_values_num[value] = 1
        else:
            field_values_num[value] += 1
    return field_values_num


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    field_values_num = count_coco_annotations_field_values(json_dict['annotations'], args.field)
    without_that_field = None
    for value, num in field_values_num.items():
        if value == 'without that field':
            without_that_field = num
            continue
        print('{} {}'.format(value, num))
    print('without that field {}'.format(without_that_field))

