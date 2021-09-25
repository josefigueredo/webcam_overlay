#!/bin/python3

__author__ = "Jose Figueredo"
__copyright__ = "Copyright 2021"
__credits__ = ["Jose Figueredo"]
__license__ = "cc0-1.0"
__version__ = "1.0.0"
__maintainer__ = "Jose Figueredo"
__email__ = "josefigueredo@gmail.com"
__status__ = "Production"


import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageQt
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QPoint, Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QBrush, QPalette, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox, QWidget


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self, video_source = 0):
        super().__init__()
        self._run_flag = True
        self.video_source = video_source

    def change_res(self, width, height):
        self.cap.set(3, width)
        self.cap.set(4, height)

    def run(self):
        # initialize webcam capture object
        self.cap = cv2.VideoCapture(self.video_source)
        
        self.change_res(320, 240)

        # capture from web cam
        while self._run_flag:
            ret, cv_img = self.cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
        # shut down capture system
        self.cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class TransparentWindow(QWidget):
    
    _disply_width = 320
    _display_height = 240
    
    def __init__(self, webcam_list):
        super().__init__()

        self.webcam_list = webcam_list
        self.webcam_selected = 0
        self.effect = False
        self.videoThread()
        self.interface()

    def interface(self):
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.image_label = QLabel(self)
        self.image_label.resize(self._disply_width, self._display_height)

        pil_image = Image.new('RGBA', (240, 240), (0, 0, 0, 0))
        ImageDraw.Draw(pil_image)
        image = Image.open("circle3.png")
        image.resize((240, 240))
        pil_image.paste(image)

        image_qt = ImageQt.toqimage(pil_image)

        pixmap = QPixmap.fromImage(image_qt)

        palette = self.palette()
        palette.setBrush(QPalette.Normal, QPalette.Window, QBrush(pixmap))
        palette.setBrush(QPalette.Inactive, QPalette.Window, QBrush(pixmap))

        self.setPalette(palette)
        self.setMask(pixmap.mask())

    def videoThread(self):
        self.thread = VideoThread(self.webcam_list[self.webcam_selected])
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        if self.effect:
            convert_to_Qt_format = convert_to_Qt_format.convertToFormat(QtGui.QImage.Format_Grayscale8)

        p = convert_to_Qt_format.scaled(self._disply_width, self._display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def drag_window(self, event):
        delta = QPoint(event.globalPos() - self.old_position)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_position = event.globalPos()
    
    def mousePressEvent(self, event):
        '''
        Right button: change source to the next posible
        Middle button: toggle black & white
        '''
        self.old_position = event.globalPos()
        self.old_position = event.globalPos()
        
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.RightButton:
                if len(self.webcam_list) > 0:
                    self.thread.stop()
                    if len(self.webcam_list) - 1 > self.webcam_selected:
                        self.webcam_selected = self.webcam_selected + 1
                    else:
                        self.webcam_selected = 0
                    self.videoThread()
            if event.button() == QtCore.Qt.MidButton:
                self.effect = not self.effect
    
    def mouseMoveEvent(self, event):
        self.drag_window(event)
        x, y = self.get_window_coordinates()
        width, height = self.get_window_size()
        region = x, y, width, height
    
    def get_window_size(self):
        size = self.frameSize().width(), self.frameSize().height()
        return size
    
    def get_window_coordinates(self):
        coordinates = self.x(), self.y()
        return coordinates
    
    def closeEvent(self, event):
        self.thread.stop()
        event.accept()
        
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.close()
            else:
                event.ignore()


def log_uncaught_exceptions(ex_cls, ex, tb):
    '''
    Shows a message box on erros
    '''
    text = '{}: {}:\n'.format(ex_cls.__name__, ex)
    import traceback
    text += ''.join(traceback.format_tb(tb))

    print(text)
    QMessageBox.critical(None, 'Error', text)
    quit()


def detect_webcams():
    '''
    The framework do not provide a function to check sources. 
    This method checks the first 5 indexes
    '''
    index = 0
    arr = []
    i = 5
    while i > 0:
        cap = cv2.VideoCapture(index)
        if cap.read()[0]:
            arr.append(index)
            cap.release()
        index += 1
        i -= 1
    return arr


def main():
    webcam_list = detect_webcams()
    if webcam_list != None:
        sys.excepthook = log_uncaught_exceptions
        app = QApplication(sys.argv)
        win = TransparentWindow(webcam_list)
        win.show()
    else:
        print('No webcams detected')
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
