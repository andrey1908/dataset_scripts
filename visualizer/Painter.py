from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGroupBox, QPushButton, QHBoxLayout, QVBoxLayout,\
                            QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QPixmap, QPainter, QPen, QFont
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from numpy import clip
from dataset_scripts.utils.coco_tools import get_category_id_to_name, get_image_id_to_annotations
import os.path as osp


class Painter(QObject):
    boxesDrawn = pyqtSignal(QGraphicsScene, bool)

    def __init__(self, json_dict, images_folder, image_idx, threshold):
        super(Painter, self).__init__()
        self.json_dict = json_dict
        self.images_folder = images_folder
        self.category_id_to_name = get_category_id_to_name(json_dict)
        self.image_id_to_annotations = get_image_id_to_annotations(json_dict)

        self.image_idx = image_idx
        self.image_file = osp.join(images_folder, json_dict['images'][image_idx]['file_name'])
        self.pixmap_item = QGraphicsPixmapItem(QPixmap(self.image_file))
        self.annotations = self.image_id_to_annotations[json_dict['images'][image_idx]['id']]
        self.threshold = threshold

    def new_image(self, image_idx):
        self.image_idx = image_idx
        self.image_file = osp.join(self.images_folder, self.json_dict['images'][image_idx]['file_name'])
        self.pixmap_item = QGraphicsPixmapItem(QPixmap(self.image_file))
        self.annotations = self.image_id_to_annotations[self.json_dict['images'][self.image_idx]['id']]
        self.draw(reset_scale=True)

    def new_threshold(self, threshold):
        self.threshold = threshold
        self.draw(reset_scale=False)

    def draw(self, reset_scale):
        scene = QGraphicsScene()
        scene.addItem(self.pixmap_item)
        for annotation in self.annotations:
            score = annotation.get('score')
            if score is not None:
                if score < self.threshold:
                    continue
            bbox = annotation['bbox']
            self.preprocess_box(bbox, self.pixmap_item.pixmap().width(), self.pixmap_item.pixmap().height())
            text = self.category_id_to_name[annotation['category_id']]
            if score is not None:
                text = text + ' {:.2f}'.format(score)
            rect_item = QGraphicsRectItem(bbox[0], bbox[1], bbox[2], bbox[3])
            text_item = QGraphicsTextItem(text)
            text_item.setPos(bbox[0], bbox[1])
            scene.addItem(rect_item)
            scene.addItem(text_item)
        self.boxesDrawn.emit(scene, reset_scale)

    def preprocess_box(self, bbox, im_w, im_h):
        bbox[2] += bbox[0]
        bbox[3] += bbox[1]
        bbox[0] = clip(bbox[0], 0, im_w)
        bbox[1] = clip(bbox[1], 0, im_h)
        bbox[2] = clip(bbox[2], 0, im_w)
        bbox[3] = clip(bbox[3], 0, im_h)
        bbox[:] = [round(b) for b in bbox]
        bbox[2] -= bbox[0]
        bbox[3] -= bbox[1]
