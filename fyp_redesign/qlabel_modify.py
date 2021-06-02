from PySide2.QtWidgets import QLabel
from PySide2.QtGui import QPainter,QPen
from PySide2.QtCore import Qt
import numpy as np
import cv2

class draw_cross(QLabel):
    x0 = -10
    y0 = -10
    flag = False
    color = ''
    info=None
    frame_data=None
    roi_hist=None
    track_window=None
    term_crit=None
    

    def mousePressEvent(self,event):
        self.flag = True
        self.x0 = event.x()
        self.y0 = event.y()

    def mouseReleaseEvent(self,event):
        # self.flag = True
        self.x0 = event.x()
        self.y0 = event.y()
        self.learn_feature()
        # self.track_window=track_window
        # self.term_crit=term_crit
        # self.roi_hist=roi_hist

    def mouseMoveEvent(self,event):
        self.x0 = event.x()
        self.y0 = event.y()
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        # rect =QRect(self.x0, self.y0, abs(self.x1-self.x0), abs(self.y1-self.y0))
        painter = QPainter(self)
        if self.color == 'red':
            painter.setPen(QPen(Qt.red,4,Qt.SolidLine))
        elif self.color == 'green':
            painter.setPen(QPen(Qt.green,4,Qt.SolidLine))
        elif self.color == 'black':
            painter.setPen(QPen(Qt.black,4,Qt.SolidLine))
        elif self.color == 'blue':
            painter.setPen(QPen(Qt.blue,4,Qt.SolidLine))
        else:
            painter.setPen(QPen(Qt.red,4,Qt.CustomDashLine))
        
        painter.drawLine(self.x0,self.y0,self.x0+10,self.y0+10)
        painter.drawLine(self.x0,self.y0,self.x0-10,self.y0+10)
        painter.drawLine(self.x0,self.y0,self.x0+10,self.y0-10)
        painter.drawLine(self.x0,self.y0,self.x0-10,self.y0-10)
        # painter.end()
        # self.update()

    def learn_feature(self):
        # data=np.array(self.frame_data.tolist())
        data=self.frame_data.asnumpy()
        r,h,c,w=self.x0,self.y0,10,10
        print(r,h,c,w)
        print('learn')
        track_window = (self.x0,self.y0,10,10)
        print(track_window)
        roi = data[r:r+h, c:c+w]
        hsv_roi =  cv2.cvtColor(data, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)))
        roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
        cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)

        # Setup the termination criteria, either 10 iteration or move by atleast 1 pt
        term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
        # return roi_hist,track_window,term_crit
        self.roi_hist=roi_hist
        self.track_window=track_window
        self.term_crit=term_crit