from PySide2 import QtWidgets
from PySide2.QtWidgets import QFileDialog
from PySide2.QtGui import QIcon, QPixmap
import numpy as np
import cv2
import fitz
import pytesseract
import sys
import csv
import dateutil.parser as dparser
import re
import os
import tempfile
from UI import main
from UI import photoeditorfinal
from UI import print
from PIL import Image, ImageEnhance,ImageQt

def _get_converted_point(user_p1, user_p2, p1, p2, x):
    """
    convert user ui slider selected value (x) to PIL value
    user ui slider scale is -100 to 100, PIL scale is -1 to 2
    example:
     - user selected 50
     - PIL value is 1.25
    """

    r = (x - user_p1) / (user_p2 - user_p1)
    return p1 + r * (p2 - p1)

def brightness(img, factor):
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(factor)

BINARY_THREHOLD = 180
def image_smoothening(img):
    ret1, th1 = cv2.threshold(img, BINARY_THREHOLD, 255, cv2.THRESH_BINARY)
    ret2, th2 = cv2.threshold(th1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    blur = cv2.GaussianBlur(th2, (1, 1), 0)
    ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th3


def remove_noise_and_smooth(file_name):
    img = cv2.imread(file_name, 0)
    # img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gaus = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 25)
    img = image_smoothening(gaus)

    return img


class MyQtApp(main.Ui_MainWindow, QtWidgets.QMainWindow, photoeditorfinal.Ui_MainWindow2):
    def __init__(self):
        super(MyQtApp, self).__init__()
        self.setupUi(self)  # to see your interface
        self.setWindowTitle("SECURE IDENTITY")
        self.pushButton_8.clicked.connect(self.browseImage)
        self.pushButton.clicked.connect(self.fileloginform)
        self.pushButton_3.clicked.connect(self.newfun)

        #self.ui.horizontalSlide.valueChanged.connect(self.update_brightness)

    def browseImage(self):
        foldername = QFileDialog.getOpenFileName(self, 'Open File', 'c\\', 'Pdf files (*.pdf)')
        pdffile = foldername[0]
        self.source_path.setText(pdffile)

    def mask(self, image_front):
        gray = cv2.cvtColor(image_front, cv2.COLOR_BGR2GRAY)
        img = cv2.GaussianBlur(gray, (3, 3), 2)
        thresh = cv2.adaptiveThreshold(img, 220, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 17, 10)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        for i in range(1, len(contours)):
            perimeter = cv2.arcLength(contours[i], True)  # true if curve is closed...perimeter means length of arc
            epsilon = 0.01 * perimeter
            approx = cv2.approxPolyDP(contours[i], epsilon,
                                      True)  # approximates a polygonal curve with specified precision

            if 13900 > cv2.contourArea(contours[i]) > 11000:
                (x, y) = thresh.shape
                mask = np.zeros((x, y, 3), np.uint8)
                mask = cv2.drawContours(mask, [approx], -1, (255, 255, 255), -1)
                mask = cv2.drawContours(mask, approx, -1, (255, 255), 5)
                result = cv2.bitwise_and(mask, image_front)

    def fileloginform(self):
        pdffile = self.source_path.text()
        password = self.lineEdit_2.text()
        doc = fitz.open(pdffile)
        page = doc.loadPage(0)
        mat = fitz.Matrix(2, 2)
        pix = page.getPixmap(matrix=mat)
        output = "outfile.png"
        output = pix.writePNG(output)

        image = cv2.imread("outfile.png")

        # cropping image____crop_img = img[y:y+h, x:x+w]
        print(image.shape)
        image = image[1140:1475, 55:1120]
        cv2.imwrite("finalimage.png", image)

        '''text = pytesseract.image_to_string(Image.open('finalimage.png'))
        print(text)'''

        image_front = image[0:355, 4:523]
        image_back = image[0:355, 544:1065]
        cv2.imwrite("image_front.png", image_front)
        

        scale_percent = 75

        # calculate the 50 percent of original dimensions
        width = int(image_front.shape[1] * scale_percent / 100)
        height = int(image_front.shape[0] * scale_percent / 100)

        # dsize
        dsize = (width, height)

        final_front = cv2.resize(image_front, dsize)
        cv2.imwrite("final_front.png", final_front)#image_front resized

        pixmap = QPixmap("final_front.png")
        self.label_4.setPixmap(QPixmap(pixmap))
        self.resize(pixmap.width(), pixmap.height())#label

        cv2.imwrite("image_back.png", image_back)

        # resizing the image
        scale_percent = 75

        # calculate the 50 percent of original dimensions
        width = int(image_back.shape[1] * scale_percent / 100)
        height = int(image_back.shape[0] * scale_percent / 100)

        # dsize
        dsize = (width, height)

        final_back = cv2.resize(image_back, dsize)
        cv2.imwrite("final_back.png", final_back)
        pixmap = QPixmap("final_back.png")
        self.label_5.setPixmap(QPixmap(pixmap))
        self.resize(pixmap.width(), pixmap.height())


        self.mask(image_front)


    def newfun(self):
        pdffile = self.source_path.text()
        doc = fitz.open(pdffile)
        page = doc.loadPage(0)
        mat = fitz.Matrix(2, 2)
        pix = page.getPixmap(matrix=mat)
        output = "outfile.png"
        output = pix.writePNG(output)

        image = cv2.imread("outfile.png")

        # cropping image____crop_img = img[y:y+h, x:x+w]
        print(image.shape)
        image = image[1140:1495, 55:1120]
        cv2.imwrite("finalimage.png", image)
        photo = image[75:205, 50:152]
        cv2.imwrite("photo.png", photo)

        scale_percent = 75

        # calculate the 50 percent of original dimensions
        width = int(photo.shape[1] * scale_percent / 100)
        height = int(photo.shape[0] * scale_percent / 100)

        # dsize
        dsize = (width, height)

        photo_final = cv2.resize(photo, dsize)
        cv2.imwrite("photo_final.png", photo_final)
        imagee = QPixmap("photo_final.png")
        self.ui.label.setPixmap(imagee)
        self.resize(imagee.width(), imagee.height())



    #def update_brightness(self,value):
        #factor = _get_converted_point(value)























if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    qt_app = MyQtApp()
    qt_app.show()
    sys.exit(app.exec_())
