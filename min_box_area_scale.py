ann_file = 'traffic_signs_detection/RTSD.json'
w, h = 1024, 576

import json

with open(ann_file, 'r') as f:
    json_dict = json.load(f)
image_id_to_shape = dict()
for image in json_dict['images']:
    image_id_to_shape[image['id']] = (image['width'], image['height'])
min_box_area_scale = 100000000
for ann in json_dict['annotations']:
    im_w, im_h = image_id_to_shape[ann['image_id']]
    scale = min(w/im_w, h/im_h)
    box_area = ann['bbox'][2] * ann['bbox'][3]
    box_area_scale = box_area * scale * scale
    min_box_area_scale = min(min_box_area_scale, box_area_scale)
print(min_box_area_scale)

