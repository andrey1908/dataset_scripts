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

