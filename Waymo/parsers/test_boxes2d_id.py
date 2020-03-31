import os
from waymo_open_dataset import dataset_pb2 as open_dataset
from dataset_scripts.utils import Context
from .registry import WAYMO_PARSERS_REGISTRY


@WAYMO_PARSERS_REGISTRY.register
class TestBoxes2DId:
    def __init__(self, context):
        self.seen_ids = set()
        self.seen_id_to_camera = dict()
        self.tfrecord_file = None
        self.out_lines = list()

    def parse(self, context):
        if self.tfrecord_file != context.tfrecord_file:
            self.seen_ids.update(self.seen_id_to_camera.keys())
            self.seen_id_to_camera.clear()
            self.tfrecord_file = context.tfrecord_file
        for labels in context.frame.camera_labels:
            if labels.name != context.image_data.name:
                continue
            for label in labels.labels:
                label_camera = self.seen_id_to_camera.get(label.id)
                if (label_camera is not None) and (label_camera != labels.name):
                    self.out_lines.append('Label with id {} appears again in an other camera\n'.format(label.id))
                if label.id in self.seen_ids:
                    self.out_lines.append('Label with id {} appears again in an other file\n'.format(label.id));
                self.seen_id_to_camera[label.id] = labels.name

    def save(self, f):
        f.writelines(self.out_lines)

