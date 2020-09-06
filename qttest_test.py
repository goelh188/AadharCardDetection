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
from PIL import Image, ImageEnhance, ImageQt


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
IMAGE_SIZE = 1800


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
        # self.ui.horizontalSlide.valueChanged.connect(self.update_brightness)

    def browseImage(self):
        """
        this function opens the dialog box.
        """
        foldername = QFileDialog.getOpenFileName(self, 'Open File', 'c\\', 'Pdf files (*.pdf)')
        pdffile = foldername[0]
        self.source_path.setText(pdffile)

    def fileloginform(self):
        """
        this function take the path of uploaded file and display it.
        """
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
        image = image[1140:1475, 55:1120]
        cv2.imwrite("finalimage.png", image)
        
        #these two images are generated from finalimage
        image_front = image[0:355, 4:523]
        image_back = image[0:355, 544:1065]
        cv2.imwrite("image_front.png", image_front)

        image_front1 = image[0:600,50:460]

        cv2.imwrite("image_front1.png",image_front1)
        image_front2 = remove_noise_and_smooth("image_front1.png")

        image_front3 = cv2.resize(image_front1, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        image_front3 = cv2.cvtColor(image_front3, cv2.COLOR_BGR2GRAY)

        #texting extract from front2 for DOB n etc
        text4 = pytesseract.image_to_string(image_front3)

        #texting extract from front2 for name
        text = pytesseract.image_to_string(image_front2)
       

        scale_percent = 75

        # calculate the 50 percent of original dimensions
        width = int(image_front.shape[1] * scale_percent / 100)
        height = int(image_front.shape[0] * scale_percent / 100)

        # dsize
        dsize = (width, height)

        final_front = cv2.resize(image_front, dsize)
        cv2.imwrite("final_front.png", final_front)  # image_front resized

        pixmap = QPixmap("final_front.png")
        self.label_4.setPixmap(QPixmap(pixmap))
        self.resize(pixmap.width(), pixmap.height())  # label

        cv2.imwrite("image_back.png", image_back)
        image_back1 = cv2.resize(image_back, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        image_back1 = cv2.cvtColor(image_back1, cv2.COLOR_BGR2GRAY)
        text3 = pytesseract.image_to_string(image_back1)#backend text extract
        print("image_back",text3)

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
    
        #text extraction from adhar
        name = None
        gender = None
        ayear = None
        aadharno = ''
        yearline = []
        genline = []
        nameline = []
        # address = []
        text1 = []
        text2 = []
        genderStr = '(Female|Male|emale|male|ale|FEMALE|MALE|EMALE)$'
        # Searching for Date of Birth
        lines = text4

        # print (lines)
        for wordlist in lines.split('\n'):
            xx = wordlist.split()
            if [w for w in xx if re.search('(Year|Birth|irth|YoB|YOB:|DOB:|DOB)$', w)]:
                yearline = wordlist
                break
            else:
                text1.append(wordlist)
        try:
            text2 = text.split(yearline, 1)[1]
        except Exception:
            pass

        try:
            if yearline:
                ayear = dparser.parse(yearline, fuzzy=True)
        except Exception:
            pass
        try:
            for wordlist in lines.split('\n'):
                xx = wordlist.split()
                if [w for w in xx if re.search(genderStr, w)]:
                    genline = wordlist
                    break

            if 'Female' in genline or 'FEMALE' in genline:
                gender = "Female"
            else:
                gender = "Male"

            text2 = text.split(genline, 1)[1]
        except Exception:
            pass
        # Search name
        try:
            newlist1 = []
            for xx in text.split('\n'):
                newlist1.append(xx)
                newlist1 = list(filter(lambda x: len(x) > 1, newlist1))
            a = 0
            str = "Government"
            str1 = "of"
            for no in newlist1:
                if str in no or str1 in no:
                    b = a
                a = a + 1
            name = newlist1[b + 2]
        except Exception:
            pass
        # Searching for VID
        vid = set()
        try:
            newlist = []
            for xx in text3.split('\n'):
                newlist.append(xx)
            newlist = list(filter(lambda x: len(x) > 12, newlist))
            for no in newlist:
                if re.match("^[VID : 0-9]+$", no):
                    g = no
                    g = g.replace("VID :", "")
                    if len(g) > 16:
                        vid.add(g)
        except Exception:
            pass

        # searching for address

        line1 = text3
        address = set()

        try:
            newlist = []
            for xx in line1.split('\n'):
                newlist.append(xx)
                newlist = list(filter(lambda x: len(x) > 5, newlist))
                a = 0
                str = "Address"
                for no in newlist:
                    a = a + 1
                    c = re.findall(r"(?<!\d)\d{6}(?!\d)", no)
                    if c:
                        d = a
                    if str in no:
                        b = a

            addre = newlist[b]
            while (b < d - 1):
                addre = addre + newlist[b + 1]
                b = b + 1

            address.add(addre)

        except Exception:
            pass

        # searching for aadhar number

        aadharno = set()
        try:

            newlist = []
            str = "XXXX"
            for xx in line1.split('\n'):
                newlist.append(xx)
                newlist = list(filter(lambda x: len(x) > 5, newlist))
                for word in newlist:
                    if re.match("^[0-9 ]+$", word) or str in word and len(word) == 12:
                        aadharno.add(word)
        except Exception:
            pass

        # Making tuples of data
        data = {}
        data['Name'] = name
        data['Gender'] = gender
        data['Birth date'] = ayear
        data['Address'] = address
        data['Aadhar number'] = aadharno
        data['vid'] = vid

        print(data)
        import pandas as pd
        df = pd.DataFrame(data=data, index=[0])
        df = (df.T)
        print(df)
        df.to_excel('dict1.xlsx')

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

    # def update_brightness(self,value):
    # factor = _get_converted_point(value)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    qt_app = MyQtApp()
    qt_app.show()
    sys.exit(app.exec_())
>>>>>>> 28a2c0a2177cdca648b2abbc01075370030ceb24
