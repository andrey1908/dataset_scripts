import argparse
import json

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def reindex_categories(categories):
    cat_id = 1
    old_cat_id_to_new = dict()
    for i in range(len(categories)):
        old_cat_id_to_new[categories[i]['id']] = cat_id
        categories[i]['id'] = cat_id
        cat_id += 1
    return old_cat_id_to_new


def reindex_images(images):
    image_id = 0
    old_image_id_to_new = dict()
    for i in range(len(images)):
        old_image_id_to_new[images[i]['id']] = image_id
        images[i]['id'] = image_id
        image_id += 1
    return old_image_id_to_new


def reindex_annotations(annotations, old_image_id_to_new, old_cat_id_to_new):
    annotation_id = 1
    for i in range(len(annotations)):
        annotations[i]['id'] = annotation_id
        annotation_id += 1
        annotations[i]['image_id'] = old_image_id_to_new[annotations[i]['image_id']]
        annotations[i]['category_id'] = old_cat_id_to_new[annotations[i]['category_id']]


def reindex_json(json_dict):
    old_cat_id_to_new = reindex_categories(json_dict['categories'])
    old_image_id_to_new = reindex_images(json_dict['images'])
    reindex_annotations(json_dict['annotations'], old_image_id_to_new, old_cat_id_to_new)


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    reindex_json(json_dict)
    with open(args.out_file, 'w') as f:
        json.dump(json_dict, f, indent=2)

