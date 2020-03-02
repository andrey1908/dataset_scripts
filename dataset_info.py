import json
import argparse


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    return parser


def get_images_shapes(json_dict, sort=False):
    images = json_dict['images']
    images_shapes = dict()
    w = 0
    h = 0
    for image in images:
        shape = (image['width'], image['height'])
        if shape not in images_shapes.keys():
            images_shapes[shape] = 0
        images_shapes[shape] += 1
        w += image['width']
        h += image['height']
    return images_shapes


def get_min_area(json_dict):
    annotations = json_dict['annotations']
    areas = list()
    for annotation in annotations:
        areas.append(annotation['area'])
    return min(areas)


def get_images_number(json_dict):
    return(len(json_dict['images']))


def get_categories_names(json_dict):
    categories_names = list()
    categories_ids = list()
    for cat in json_dict['categories']:
        categories_names.append(cat['name'])
        categories_ids.append(cat['id'])
    categories_ids, categories_names = zip(*sorted(list(zip(categories_ids, categories_names))))
    return categories_names


def get_categories_number(json_dict):
    cat_id_to_name = dict()
    categories_number = dict()
    for cat in json_dict['categories']:
        cat_id_to_name[cat['id']] = cat['name']
        categories_number[cat['name']] = 0
    for ann in json_dict['annotations']:
        categories_number[cat_id_to_name[ann['category_id']]] += 1
    return categories_number


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)

    img_num = get_images_number(json_dict)
    print("Images number: {}\n".format(img_num))

    print("Images shapes:")
    images_shapes = get_images_shapes(json_dict)
    for image_shape in images_shapes.keys():
        print(image_shape, " {}".format(images_shapes[image_shape]))
    print("")

    categories_number = get_categories_number(json_dict)
    print("Categories number:")
    for cat_name in categories_number.keys():
        print("{} {}".format(cat_name, categories_number[cat_name]))
    print("")
        
