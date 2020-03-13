import argparse
import json
from reindex_json import reindex_json
import re


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-new-cats', '--new-categories-names', required=True, type=str, nargs='+')
    parser.add_argument('-old-cat-name-to-new', '--old-category-name-to-new', required=True, type=str)
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def get_new_categories(new_categories_names):
    new_categories = list()
    new_category_name_to_id = dict()
    cat_id = 1
    for new_cat_name in new_categories_names:
        new_cat = {"supercategory": "none", "id": cat_id, "name": new_cat_name}
        new_categories.append(new_cat)
        new_category_name_to_id[new_cat_name] = cat_id
        cat_id += 1
    return new_categories, new_category_name_to_id


def replace_categories(old_categories, new_categories_names, old_category_name_to_new):
    new_categories, new_category_name_to_id = get_new_categories(new_categories_names)
    old_category_id_to_new = dict()
    for old_category in old_categories:
        if old_category['name'] in old_category_name_to_new.keys():
            old_category_id_to_new[old_category['id']] = new_category_name_to_id[old_category_name_to_new[old_category['name']]]
    old_categories[:] = new_categories
    return old_category_id_to_new


def correct_annotations(annotations, old_category_id_to_new):
    for i in range(len(annotations)-1,-1,-1):
        if annotations[i]['category_id'] not in old_category_id_to_new.keys():
            del annotations[i]
            continue
        annotations[i]['category_id'] = old_category_id_to_new[annotations[i]['category_id']]


def convert_all_categories(catgories, new_name):
    old_category_name_to_new = dict()
    for category in catgories:
        old_name = category['name']
        old_category_name_to_new[old_name] = new_name
    return old_category_name_to_new


def replace_classes(json_dict, new_categories_names, old_category_name_to_new):
    if type(old_category_name_to_new) == str:
        if old_category_name_to_new == 'conv_all_cats':
            assert(len(new_categories_names) == 1)
            old_category_name_to_new = convert_all_categories(json_dict['categories'], new_categories_names[0])
        else:
            raise NotImplementedError()
    old_category_id_to_new = replace_categories(json_dict['categories'], new_categories_names, old_category_name_to_new)
    correct_annotations(json_dict['annotations'], old_category_id_to_new)
    reindex_json(json_dict)


def parse_old_category_name_to_new(args_old_category_name_to_new):
    if (args_old_category_name_to_new == 'convert_all_categories') or (args_old_category_name_to_new == 'conv_all_cats'):
        return 'conv_all_cats'
    old_category_name_to_new = dict()
    args_old_category_name_to_new = args_old_category_name_to_new.split(' ')
    for one_convertion in args_old_category_name_to_new:
        old_name, new_name = re.split('->', one_convertion)
        old_category_name_to_new[old_name] = new_name
    return old_category_name_to_new


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    old_category_name_to_new = parse_old_category_name_to_new(args.old_category_name_to_new)
    replace_classes(json_dict, args.new_categories_names, old_category_name_to_new)
    with open(args.out_file, 'w') as f:
        json.dump(json_dict, f, indent=2)

