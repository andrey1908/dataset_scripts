import os
from utils import Context
from .registry import WAYMO_PARSERS_REGISTRY
from pathlib import Path


@WAYMO_PARSERS_REGISTRY.register
class Track2DParser:
    requirements = ('ImagesParser', 'Boxes2DParser')

    class Sequence:
        def __init__(self, sequence_id):
            self.sequence_id = sequence_id
            self.images_files = list()
            self.labels_ids = list()
            self.labels_types = list()
            self.labels_boxes = list()

        def add(self, image_file, label_id, label_type, label_box):
            self.images_files.append(image_file)
            self.labels_ids.append(label_id)
            self.labels_types.append(label_type)
            self.labels_boxes.append(label_box)

        def save(self, out_folder, sequence_name_max_len):
            if len(self.images_files) <= 1:
                return None, None
            common_path = os.path.normpath(os.path.commonpath(self.images_files))
            out_lines = list()
            for image_file, label_id, label_type, label_box in zip(self.images_files, self.labels_ids, self.labels_types, self.labels_boxes):  
                out_line = '{} {} {} {} {} {} {}\n'.format(os.path.relpath(image_file, common_path), label_id, label_type,
                                                           label_box[0], label_box[1], label_box[2], label_box[3])
                out_lines.append(out_line)
            out_file = 'sequence_' + str(self.sequence_id).zfill(sequence_name_max_len) + '.txt'
            out_file = os.path.join(out_folder, out_file)
            with open(out_file, 'w') as f:
                f.writelines(out_lines)
            return out_file, common_path

    def __init__(self, context):
        if not context.valid_attr('out_track_folder'):
            raise RuntimeError('TrackBoxes2DParser requires out_track_folder specified')
        Path(context.out_track_folder).mkdir(parents=True, exist_ok=True)
        self.sequences = dict()
        self.sequence_name_max_len = 4
        self.label_type_to_str = {1: 'vehicle', 2: 'pedestrian', 3: 'sign', 4: 'cyclist'}

    def parse(self, context):
        sequence_name = context.frame.context.name
        camera_id = context.image_data.name
        sequence_and_label_id_to_int = self.sequences.get((sequence_name, camera_id))
        if sequence_and_label_id_to_int is None:
            sequence = self.Sequence(len(self.sequences))
            label_id_to_int = dict()
            sequence_and_label_id_to_int = (sequence, label_id_to_int)
            self.sequences[(sequence_name, camera_id)] = sequence_and_label_id_to_int
        sequence, label_id_to_int = sequence_and_label_id_to_int
        image_file = context.ImagesParser_context.image_file
        for label_id, label_type, label_box in zip(context.Boxes2DParser_context.ids,
                                                   context.Boxes2DParser_context.types, context.Boxes2DParser_context.boxes):
            label_id_int = label_id_to_int.get(label_id, len(label_id_to_int))
            if label_id_int == len(label_id_to_int):
                label_id_to_int[label_id] = label_id_int
            label_type_str = self.label_type_to_str[label_type]
            sequence.add(image_file, label_id_int, label_type_str, label_box)

    def save(self, out_file, context):
        out_lines = self._save_sequences(context)
        with open(out_file, 'w') as f:
            f.writelines(out_lines)

    def _save_sequences(self, context):
        out_lines = list()
        track_root_folder = context.track_root_folder if context.valid_attr('track_root_folder') else context.out_track_folder
        images_root_folder = context.images_root_folder if context.valid_attr('images_root_folder') is None else context.out_images_folder
        for sequence, _ in self.sequences.values():
            sequence_file, images_path = sequence.save(context.out_track_folder, self.sequence_name_max_len)
            if (sequence_file is None) or (images_path is None):
                continue
            out_line = '{} {}\n'.format(os.path.relpath(sequence_file, track_root_folder), os.path.relpath(images_path, images_root_folder))
            out_lines.append(out_line)
        return out_lines

