import numpy as np


def get_image_id_to_idx(json_dict):
    image_id_to_idx = dict()
    for i, image in enumerate(json_dict['images']):
        image_id_to_idx[image['id']] = i
    return image_id_to_idx


def get_annotation_id_to_image_idx(json_dict):
    annotation_id_to_image_idx = dict()
    image_id_to_idx = get_image_id_to_idx(json_dict)
    for ann in json_dict['annotations']:
        annotation_id_to_image_idx[ann['id']] = image_id_to_idx[ann['image_id']]
    return annotation_id_to_image_idx


def get_image_id_to_annotations_idxs(json_dict):
    image_id_to_annotations_idxs = dict()
    for image in json_dict['images']:
        image_id_to_annotations_idxs[image['id']] = list()
    for i, annotation in enumerate(json_dict['annotations']):
        image_id_to_annotations_idxs[annotation['image_id']].append(i)
    return image_id_to_annotations_idxs


def get_image_id_to_annotations(json_dict):
    image_id_to_annotations = dict()
    for image in json_dict['images']:
        image_id_to_annotations[image['id']] = list()
    for i, annotation in enumerate(json_dict['annotations']):
        image_id_to_annotations[annotation['image_id']].append(annotation)
    return image_id_to_annotations


def get_category_id_to_name(json_dict):
    category_id_to_name = dict()
    for category in json_dict['categories']:
        category_id_to_name[category['id']] = category['name']
    return category_id_to_name


def find_image_by_name(json_dict, file_name):
    for image in json_dict['images']:
        if image['file_name'] == file_name:
            return image
    return None


def leave_annotations(annotations, idxs_to_leave):
    np_annotations = np.array(annotations)
    annotations[:] = np_annotations[idxs_to_leave]
    annotation_id = 1
    for i in range(len(annotations)):
        annotations[i]['id'] = annotation_id
        annotation_id += 1


def leave_boxes(json_dict, area, width=None, height=None):
    if area[1] == -1:
        area = (area[0], 1e5**2)
    if (width is not None) and (height is not None):
        use_scale = True
    else:
        use_scale = False
    image_id_to_idx = get_image_id_to_idx(json_dict)
    idxs_to_leave = list()
    for i in range(len(json_dict['annotations'])):
        if use_scale:
            image_idx = image_id_to_idx[json_dict['annotations'][i]['image_id']]
            image = json_dict['images'][image_idx]
            scale = min(width / image['width'], height / image['height'])
            S = json_dict['annotations'][i]['area'] * scale * scale
        else:
            S = json_dict['annotations'][i]['area']
        if (S >= area[0]) and (S <= area[1]):
            idxs_to_leave.append(i)
    removed = len(json_dict['annotations']) - len(idxs_to_leave)
    leave_annotations(json_dict['annotations'], idxs_to_leave)
    return removed

