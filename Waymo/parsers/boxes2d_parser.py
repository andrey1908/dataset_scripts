import os
import json
from dataset_scripts.utils import Context
from .registry import WAYMO_PARSERS_REGISTRY


@WAYMO_PARSERS_REGISTRY.register
class Boxes2DParser:
    requirements = ('ImagesParser',)

    def __init__(self, context):
        self.json_dict = {'images': list(), 'annotations': list(), 'categories': self._get_categories()}
        self.image_id = 0
        self.ann_id = 1

    def _get_categories(self):
        categories = [{'id': 1, 'name': 'vehicle'},
                      {'id': 2, 'name': 'pedestrian'},
                      {'id': 3, 'name': 'cyclist'}]
        return categories

    def _conv_cat_id(self, cat_id):
        if cat_id == 1:
            return 1
        elif cat_id == 2:
            return 2
        elif cat_id == 4:
            return 3
        else:
            raise RuntimeError

    def parse(self, context):
        Boxes2DParser_context = Context(boxes=list(), types=list(), ids=list())
        for labels in context.frame.camera_labels:
            if labels.name != context.image_data.name:
                continue
            for label in labels.labels:
                ann = dict()
                bbox = [label.box.center_x-label.box.length/2, label.box.center_y-label.box.width/2,
                        label.box.length, label.box.width]
                ann['area'] = bbox[2] * bbox[3]
                ann['iscrowd'] = 0
                ann['image_id'] = self.image_id
                ann['bbox'] = bbox
                ann['category_id'] = self._conv_cat_id(label.type)
                ann['id'] = self.ann_id
                self.json_dict['annotations'].append(ann)
                self.ann_id += 1
                Boxes2DParser_context.boxes.append(bbox)
                Boxes2DParser_context.types.append(label.type)
                Boxes2DParser_context.ids.append(label.id)
        images_root_folder = context.images_root_folder if context.valid_attr('images_root_folder') else context.out_images_folder
        file_name = os.path.relpath(context.ImagesParser_context.image_file, images_root_folder)
        image = {'file_name': file_name, 'id': self.image_id,
                 'width': context.ImagesParser_context.image_width, 'height': context.ImagesParser_context.image_height}
        self.json_dict['images'].append(image)
        self.image_id += 1
        context.update(Boxes2DParser_context=Boxes2DParser_context)

    def save(self, out_file, context):
        with open(out_file, 'w') as f:
            json.dump(self.json_dict, f, indent=2)

