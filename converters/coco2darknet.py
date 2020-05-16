import argparse
import os
import json
from pathlib import Path
from dataset_scripts.utils.coco_tools import get_image_id_to_annotations_idxs


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-img-root-fld', '--images-root-folder', required=True, type=str)
    parser.add_argument('-out-list', '--out-list-file', required=True, type=str)
    parser.add_argument('-out-anns-fld', '--out-annotations-folder', required=True, type=str)
    parser.add_argument('-root-fld', '--root-folder', type=str, default='./')
    return parser


def coco2darknet(json_file, images_root_folder, out_list_file, out_annotations_folder, root_folder):
    with open(json_file, 'r') as f:
        json_dict = json.load(f)
    images = json_dict['images']
    image_id_to_annotations_idxs = get_image_id_to_annotations_idxs(json_dict)
    out_list = list()
    Path(out_annotations_folder).mkdir(parents=True, exist_ok=True)
    for image in images:
        out_list.append(os.path.relpath(os.path.join(images_root_folder, image['file_name']), root_folder) + '\n')
        lines = list()
        for annotation_idx in image_id_to_annotations_idxs[image['id']]:
            annotation = json_dict['annotations'][annotation_idx]
            line = '{} {} {} {} {}\n'.format(annotation['category_id']-1,
                                             (annotation['bbox'][0] + annotation['bbox'][2]/2)/image['width'],
                                             (annotation['bbox'][1] + annotation['bbox'][3]/2)/image['height'],
                                             annotation['bbox'][2]/image['width'], annotation['bbox'][3]/image['height'])
            lines.append(line)
        if len(lines) > 0:
            lines[-1] = lines[-1][:-1]
        file_name = os.path.join(out_annotations_folder, os.path.basename(image['file_name']))
        file_name = os.path.splitext(file_name)[0]+'.txt'
        with open(file_name, 'w') as f:
            f.writelines(lines)
    out_list[-1] = out_list[-1][:-1]
    with open(out_list_file, 'w') as f:
        f.writelines(out_list)


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    coco2darknet(**vars(args))

