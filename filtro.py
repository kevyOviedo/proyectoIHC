from PyQt5 import QtWidgets, QtGui, QtCore
import numpy as np

class StaticOverlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool |
            QtCore.Qt.WindowTransparentForInput
        )

        screen = QtWidgets.QApplication.primaryScreen().size()
        self.resize(screen)
        self.width_, self.height_ = self.size().width(), self.size().height()

        self.circle_pos = QtCore.QPoint(self.width_ // 2, self.height_ // 2)
        self.radius = 400
        self.fade = 50

        self.static_img = QtGui.QImage()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(40)

    @QtCore.pyqtSlot(float, float)
    def update_eye_pos(self, x, y):
        self.circle_pos = QtCore.QPoint(int(x), int(y))

    def update_frame(self):
        noise = np.random.randint(0, 256, (self.height_, self.width_), dtype=np.uint8)
        qimg = QtGui.QImage(noise.data, self.width_, self.height_, self.width_, QtGui.QImage.Format_Grayscale8)

        static_colored = QtGui.QImage(self.width_, self.height_, QtGui.QImage.Format_ARGB32_Premultiplied)
        painter = QtGui.QPainter(static_colored)
        painter.drawImage(0, 0, qimg)

        mask = QtGui.QImage(self.width_, self.height_, QtGui.QImage.Format_ARGB32_Premultiplied)
        mask.fill(QtCore.Qt.transparent)
        mask_painter = QtGui.QPainter(mask)

        gradient = QtGui.QRadialGradient(self.circle_pos, self.radius + self.fade)
        gradient.setColorAt(0.0, QtGui.QColor(0, 0, 0, 0))
        gradient.setColorAt(self.radius / (self.radius + self.fade), QtGui.QColor(0, 0, 0, 0))
        gradient.setColorAt(1.0, QtGui.QColor(0, 0, 0, 255))

        mask_painter.setBrush(QtGui.QBrush(gradient))
        mask_painter.setPen(QtCore.Qt.NoPen)
        mask_painter.drawRect(0, 0, self.width_, self.height_)
        mask_painter.end()

        painter.setCompositionMode(QtGui.QPainter.CompositionMode_DestinationIn)
        painter.drawImage(0, 0, mask)
        painter.end()

        self.static_img = static_colored
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self.static_img)

    def close_overlay(self):
        self.close()

    