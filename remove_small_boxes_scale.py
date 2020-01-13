import argparse
import json


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-thr', '--threshold', required=True, type=float)  # 55
    parser.add_argument('-out', '--out-file', required=True, type=str)
    return parser


def get_image_id_to_image(json_dict):
    image_id_to_image = dict()
    for image in json_dict['images']:
        image_id_to_image[image['id']] = image
    return image_id_to_image


def remove_small_boxes_scale(json_dict, threshold, image_id_to_image):
    sub = 0
    for i in range(len(json_dict['annotations'])):
        image = image_id_to_image[json_dict['annotations'][i - sub]['image_id']]
        scale = min(640/image['width'], 384/image['height'])
        if json_dict['annotations'][i - sub]['area'] * scale * scale < threshold:
            del json_dict['annotations'][i - sub]
            sub += 1
        else:
            json_dict['annotations'][i - sub]['id'] -= sub
    return sub


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    image_id_to_image = get_image_id_to_image(json_dict)
    removed = remove_small_boxes_scale(json_dict, args.threshold, image_id_to_image)
    print('Removed {} boxes'.format(removed))
    with open(args.out_file, 'w') as f:
        json.dump(json_dict, f, indent=2)

