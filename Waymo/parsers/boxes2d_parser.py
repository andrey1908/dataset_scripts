import os
import json
from waymo_open_dataset import dataset_pb2 as open_dataset
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
                      {'id': 3, 'name': 'sign'},
                      {'id': 4, 'name': 'cyclist'}]
        return categories

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
                ann['category_id'] = label.type
                ann['id'] = self.ann_id
                self.json_dict['annotations'].append(ann)
                self.ann_id += 1
                Boxes2DParser_context.boxes.append(bbox)
                Boxes2DParser_context.types.append(label.type)
                Boxes2DParser_context.ids.append(label.id)
        root_folder = context.root_folder if context.valid_attr('root_folder') else context.out_images_folder
        file_name = os.path.relpath(context.ImagesParser_context.image_file, root_folder)
        image = {'file_name': file_name, 'id': self.image_id,
                 'width': context.ImagesParser_context.image_width, 'height': context.ImagesParser_context.image_height}
        self.json_dict['images'].append(image)
        self.image_id += 1
        context.update(Boxes2DParser_context=Boxes2DParser_context)

    def save(self, f):
        json.dump(self.json_dict, f, indent=2)

