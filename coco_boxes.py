import argparse
import json


def get_image_id_to_image(json_dict):
    image_id_to_image = dict()
    for image in json_dict['images']:
        image_id_to_image[image['id']] = image
    return image_id_to_image


def leave_boxes_scale(json_dict, area, width, height):
    if area[1] == -1:
        area = (area[0], 1e5**2)
    image_id_to_image = get_image_id_to_image(json_dict)
    sub = 0
    for i in range(len(json_dict['annotations'])):
        image = image_id_to_image[json_dict['annotations'][i - sub]['image_id']]
        scale = min(width/image['width'], height/image['height'])
        S = json_dict['annotations'][i - sub]['area'] * scale * scale
        if (S < area[0]) or (S > area[1]):
            del json_dict['annotations'][i - sub]
            sub += 1
        else:
            json_dict['annotations'][i - sub]['id'] -= sub
    return sub


def leave_boxes(json_dict, area):
    if area[1] == -1:
        area = (area[0], 1e5**2)
    image_id_to_image = get_image_id_to_image(json_dict)
    sub = 0
    for i in range(len(json_dict['annotations'])):
        image = image_id_to_image[json_dict['annotations'][i - sub]['image_id']]
        S = json_dict['annotations'][i - sub]['area']
        if (S < area[0]) or (S > area[1]):
            del json_dict['annotations'][i - sub]
            sub += 1
        else:
            json_dict['annotations'][i - sub]['id'] -= sub
    return sub


if __name__ == '__main__':
    raise NotImplementedError

