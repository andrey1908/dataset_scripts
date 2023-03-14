import os
import os.path as osp
import numpy as np
import cv2
from tqdm import tqdm


class_id_to_name = \
{
    0: 'Bird',
    1: 'Ground Animal',
    2: 'Curb',
    3: 'Fence',
    4: 'Guard Rail',
    5: 'Barrier',
    6: 'Wall',
    7: 'Bike Lane',
    8: 'Crosswalk - Plain',
    9: 'Curb Cut',
    10: 'Parking',
    11: 'Pedestrian Area',
    12: 'Rail Track',
    13: 'Road',
    14: 'Service Lane',
    15: 'Sidewalk',
    16: 'Bridge',
    17: 'Building',
    18: 'Tunnel',
    19: 'Person',
    20: 'Bicyclist',
    21: 'Motorcyclist',
    22: 'Other Rider',
    23: 'Lane Marking - Crosswalk',
    24: 'Lane Marking - General',
    25: 'Mountain',
    26: 'Sand',
    27: 'Sky',
    28: 'Snow',
    29: 'Terrain',
    30: 'Vegetation',
    31: 'Water',
    32: 'Banner',
    33: 'Bench',
    34: 'Bike Rack',
    35: 'Billboard',
    36: 'Catch Basin',
    37: 'CCTV Camera',
    38: 'Fire Hydrant',
    39: 'Junction Box',
    40: 'Mailbox',
    41: 'Manhole',
    42: 'Phone Booth',
    43: 'Pothole',
    44: 'Street Light',
    45: 'Pole',
    46: 'Traffic Sign Frame',
    47: 'Utility Pole',
    48: 'Traffic Light',
    49: 'Traffic Sign (Back)',
    50: 'Traffic Sign (Front)',
    51: 'Trash Can',
    52: 'Bicycle',
    53: 'Boat',
    54: 'Bus',
    55: 'Car',
    56: 'Caravan',
    57: 'Motorcycle',
    58: 'On Rails',
    59: 'Other Vehicle',
    60: 'Trailer',
    61: 'Truck',
    62: 'Wheeled Slow',
    63: 'Car Mount',
    64: 'Ego Vehicle',
    65: 'Unlabeled'
}


class_name_to_id = \
{
    'Banner': 32,
    'Barrier': 5,
    'Bench': 33,
    'Bicycle': 52,
    'Bicyclist': 20,
    'Bike Lane': 7,
    'Bike Rack': 34,
    'Billboard': 35,
    'Bird': 0,
    'Boat': 53,
    'Bridge': 16,
    'Building': 17,
    'Bus': 54,
    'CCTV Camera': 37,
    'Car': 55,
    'Car Mount': 63,
    'Caravan': 56,
    'Catch Basin': 36,
    'Crosswalk - Plain': 8,
    'Curb': 2,
    'Curb Cut': 9,
    'Ego Vehicle': 64,
    'Fence': 3,
    'Fire Hydrant': 38,
    'Ground Animal': 1,
    'Guard Rail': 4,
    'Junction Box': 39,
    'Lane Marking - Crosswalk': 23,
    'Lane Marking - General': 24,
    'Mailbox': 40,
    'Manhole': 41,
    'Motorcycle': 57,
    'Motorcyclist': 21,
    'Mountain': 25,
    'On Rails': 58,
    'Other Rider': 22,
    'Other Vehicle': 59,
    'Parking': 10,
    'Pedestrian Area': 11,
    'Person': 19,
    'Phone Booth': 42,
    'Pole': 45,
    'Pothole': 43,
    'Rail Track': 12,
    'Road': 13,
    'Sand': 26,
    'Service Lane': 14,
    'Sidewalk': 15,
    'Sky': 27,
    'Snow': 28,
    'Street Light': 44,
    'Terrain': 29,
    'Traffic Light': 48,
    'Traffic Sign (Back)': 49,
    'Traffic Sign (Front)': 50,
    'Traffic Sign Frame': 46,
    'Trailer': 60,
    'Trash Can': 51,
    'Truck': 61,
    'Tunnel': 18,
    'Unlabeled': 65,
    'Utility Pole': 47,
    'Vegetation': 30,
    'Wall': 6,
    'Water': 31,
    'Wheeled Slow': 62
}


classes_remap = \
{
    'Bicyclist': 'person',
    'Bus': 'vehicle',
    'Car': 'vehicle',
    'Caravan': 'vehicle',
    'Ego Vehicle': 'ego_vehicle',
    'Motorcyclist': 'person',
    'Other Rider': 'person',
    'Other Vehicle': 'vehicle',
    'Person': 'person',
    'Trailer': 'vehicle',
    'Truck': 'vehicle'
}


remapped_class_name_to_id = \
{
    'person': 0,
    'vehicle': 1,
    'ego_vehicle': 2
}


def get_masks(label):
    objects = set(label.ravel())
    masks = list()
    for obj in objects:
        class_id = ((obj >> 8) & 0xFF)
        class_name = class_id_to_name[class_id]
        if class_name not in classes_remap:
            continue
        remapped_class_id = remapped_class_name_to_id[classes_remap[class_name]]
        mask = np.zeros(label.shape, dtype=np.uint8)
        roi = (obj == label)
        mask[roi] = 1
        masks.append((remapped_class_id, mask))
    return masks


def to_single_polygon(polygons):
    if len(polygons) == 1:
        return polygons[0]

    single_polygon = np.empty((0, 1, 2))
    for polygon in polygons:
        single_polygon = \
            np.concatenate((single_polygon, polygon, polygon[:1, :, :]), axis=0)
    return single_polygon


def get_polygons(masks):
    polygons = list()
    for class_id, mask in masks:
        multiple_polygons, _ = \
            cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        polygon = to_single_polygon(multiple_polygons)
        polygons.append((class_id, polygon))

    if len(polygons) == 0:
        return None
    return polygons


def save_polygons(path, polygons, width, height):
    out = str()
    for class_id, polygon in polygons:
        out += f"{class_id}"
        x = polygon[:, 0, 0] / width
        y = polygon[:, 0, 1] / height
        for coords in np.dstack((x, y))[0]:
            out += f" {coords[0]:.5f} {coords[1]:.5f}"
        out += "\n"

    out = out[:-1]
    with open(path, 'w') as f:
        f.write(out)


def parse_folder(path, out_path):
    os.makedirs(out_path, exist_ok=True)

    images_paths = sorted(os.listdir(osp.join(path, "images")))
    instances_paths = sorted(os.listdir(osp.join(path, "instances")))
    assert len(images_paths) == len(instances_paths)

    images_paths = list(map(lambda x: osp.join(path, "images", x), images_paths))
    instances_paths = list(map(lambda x: osp.join(path, "instances", x), instances_paths))

    total = 0
    success = 0
    for instance_path in tqdm(instances_paths):
        # print(instance_path)
        label = cv2.imread(instance_path, cv2.IMREAD_UNCHANGED)
        masks = get_masks(label)
        polygons = get_polygons(masks)
        if polygons is not None:
            width = label.shape[1]
            height = label.shape[0]
            save_polygons(
                osp.join(out_path, osp.basename(instance_path).replace('.png', '.txt')),
                polygons, width, height)
            success += 1
        total += 1
    print(success)
    print(total)


path = "/media/cds-jetson-host/data/Mapillary/An_o5cmHOsS1VbLdaKx_zfMdi0No5LUpL2htRxMwCjY_bophtOkM0-6yTKB2T2sa0yo1oP086sqiaCjmNEw5d_pofWyaE9LysYJagH8yXw_GZPzK2wfiQ9u4uAKrVcEIrkJiVuTn7JBumrA"
train_path = osp.join(path, "training")
val_path = osp.join(path, "validation")

parse_folder(train_path, osp.join(train_path, "ultralytics"))
parse_folder(val_path, osp.join(val_path, "ultralytics"))
