import os
from pathlib import Path
from PIL import Image
import tensorflow as tf
from waymo_open_dataset import dataset_pb2 as open_dataset
from dataset_scripts.utils import Context
from .registry import WAYMO_PARSERS_REGISTRY


@WAYMO_PARSERS_REGISTRY.register
class ImagesParser:
    def __init__(self, context):
        self.camera_id_to_name = self._get_camera_id_to_name()
        self.images_num = dict()
        #woe means without extension
        tfrecord_files_woe = list()
        for tfrecord_file in context.tfrecord_files:
            tfrecord_files_woe.append(os.path.splitext(tfrecord_file)[0])
        self.common_path = os.path.commonpath(tfrecord_files_woe)

    def _get_camera_id_to_name(self):
        name_id_items = open_dataset.CameraName.Name.items()
        names_and_ids = list(zip(*name_id_items))
        id_name_items = list(zip(names_and_ids[1], names_and_ids[0]))
        camera_id_to_name = dict(id_name_items)
        return camera_id_to_name

    def parse(self, context):
        if context.new_tfrecord_file:
            self.images_num.clear()
            tfrecord_file_woe = os.path.splitext(context.tfrecord_file)[0]
            self.relpath_to_save = os.path.relpath(tfrecord_file_woe, self.common_path)
        image_feature = self._get_image_feature(context)
        image_num = self.images_num.get(image_feature, 0)
        path_to_save_image = os.path.join(context.out_images_folder, self.relpath_to_save, image_feature, '{}.jpg'.format(image_num))
        path_to_save_image = os.path.normpath(path_to_save_image)
        self.images_num[image_feature] = image_num + 1
        if context.save_images:
            if os.path.isfile(path_to_save_image):
                raise RuntimeError('Image {} already exists'.format(path_to_save_image))
            Path(os.path.dirname(path_to_save_image)).mkdir(parents=True, exist_ok=True)
            im = Image.fromarray(tf.image.decode_jpeg(context.image_data.image).numpy())
            im.save(path_to_save_image)
            image_width, image_height = im.size[0], im.size[1]
        else:
            if not os.path.isfile(path_to_save_image):
                raise RuntimeError('Image {} does not exist'.format(path_to_save_image))
            im = tf.image.decode_jpeg(context.image_data.image)
            image_width, image_height = int(im.shape[1]), int(im.shape[0])
        ImagesParser_context = Context(image_file=path_to_save_image, image_width=image_width, image_height=image_height)
        context.update(ImagesParser_context=ImagesParser_context)

    def _get_image_feature(self, context):
        if (context.images_feature_name is None) or (context.images_feature_name == ''):
            feature = ''
        elif context.images_feature_name == 'camera':
            feature = self.camera_id_to_name[context.image_data.name]
        return feature

