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


def get_annotations_number(json_dict):
    cat_id_to_name = dict()
    annotations_number = dict()
    for cat in json_dict['categories']:
        cat_id_to_name[cat['id']] = cat['name']
        annotations_number[cat['name']] = 0
    for ann in json_dict['annotations']:
        annotations_number[cat_id_to_name[ann['category_id']]] += 1
    return annotations_number


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)

    img_num = get_images_number(json_dict)
    print("Images number: {}\n".format(img_num))

    print("Images shapes:")
    images_shapes = get_images_shapes(json_dict)
    images_shapes_nums = list(images_shapes.items())
    images_shapes_nums.sort(key=lambda x: -x[1])
    for image_shape, num in images_shapes_nums:
        print(image_shape, " {}".format(num))
    print("")

    annotations_number = get_annotations_number(json_dict)
    print("Annotations number:")
    for cat_name in annotations_number.keys():
        print("{} {}".format(cat_name, annotations_number[cat_name]))
    print("")

    annotations_number_in_total = len(json_dict['annotations'])
    print("Annotations number in total: {}".format(annotations_number_in_total))
    print("")

