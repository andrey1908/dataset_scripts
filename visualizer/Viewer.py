from PyQt5.QtWidgets import QApplication, QWidget, QToolButton, QLineEdit, QVBoxLayout, QHBoxLayout, QGraphicsView,\
                            QGraphicsScene, QGraphicsPixmapItem, QFrame, QGroupBox, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QPixmap, QBrush, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QPoint, QRectF, pyqtSignal, QPointF


class Viewer(QGroupBox):
    scaleChanged = pyqtSignal(float)

    def __init__(self, width, height):
        super(Viewer, self).__init__('Viewer')
        self.width = width
        self.height = height
        self.zoom = 0
        self.scale = -1
        self.labels_poses = list()
        self.pixmap_size = tuple()
        self.pen = QPen(Qt.red)
        self.font = QFont('Decorative')
        self.pen_width = 2
        self.font_size = 13
        self.init_UI()

    def init_UI(self):
        self.view = QGraphicsView()
        self.view.wheelEvent = self.wheelEvent
        self.view.setFixedSize(self.width, self.height)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        # self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setBackgroundBrush(QBrush(QColor(0, 0, 0)))
        self.view.setFrameShape(QFrame.NoFrame)
        vbox = QVBoxLayout()
        vbox.addWidget(self.view)
        self.setLayout(vbox)

    def set_scene(self, scene, reset_scale):
        self.labels_poses = list()
        for item in scene.items():
            if isinstance(item, QGraphicsTextItem):
                self.labels_poses.append(item.pos())
            elif isinstance(item, QGraphicsPixmapItem):
                self.pixmap_size = (item.pixmap().width(), item.pixmap().height())
        self.view.setScene(scene)
        if reset_scale:
            self.reset_scale()
        else:
            self.apply_style()

    def reset_scale(self):
        if self.view.scene() is None:
            return
        self.view.setSceneRect(QRectF(0, 0, self.pixmap_size[0], self.pixmap_size[1]))
        unity = self.view.transform().mapRect(QRectF(0, 0, 1, 1))
        self.view.scale(1 / unity.width(), 1 / unity.height())
        factor = min(self.width / self.pixmap_size[0], self.height / self.pixmap_size[1])
        self.view.scale(factor, factor)
        self.scale = factor
        self.adjust_size()
        self.zoom = 0

    def apply_style(self):
        label_idx = 0
        for item in self.view.scene().items():
            if isinstance(item, QGraphicsRectItem):
                item.setPen(self.pen)
            elif isinstance(item, QGraphicsTextItem):
                item.setFont(self.font)
                item.setDefaultTextColor(Qt.red)
                item.document().setDocumentMargin(0)
                item.document().adjustSize()
                dx = min(self.pixmap_size[0] - self.labels_poses[label_idx].x() - item.document().size().width(), 0)
                dy = max(-self.labels_poses[label_idx].y(), -item.document().size().height())
                item.setPos(self.labels_poses[label_idx] + QPointF(dx, dy))
                label_idx += 1
            else:
                assert isinstance(item, QGraphicsPixmapItem)

    def adjust_size(self):
        self.pen.setWidthF(max(self.pen_width / self.scale, 1))
        self.font.setPointSizeF(max(self.font_size / self.scale, 1))
        self.apply_style()

    def wheelEvent(self, event):
        if self.view.scene() is None:
            return
        if event.angleDelta().y() > 0:
            factor = 1.25
            self.zoom += 1
        else:
            factor = 0.8
            self.zoom -= 1

        if self.zoom > 0:
            self.view.scale(factor, factor)
            self.scale *= factor
            self.adjust_size()
        elif self.zoom == 0:
            self.reset_scale()
        else:
            self.zoom = 0
