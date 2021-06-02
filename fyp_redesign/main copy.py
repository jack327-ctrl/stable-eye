from pickle import NONE
import sys
import operator
from moviepy.editor import VideoFileClip
from numpy.lib.npyio import load
from main_fyp import Ui_MainWindow
from PySide2.QtWidgets import QApplication, QScrollBar,QWidget,QLabel
from PySide2.QtWidgets import QMainWindow, QFileDialog
from PySide2.QtWidgets import QMessageBox
from PySide2.QtGui import QImage, QPixmap, QPainter, QPen, QGuiApplication,QColor,QIcon
from PySide2.QtCore import QTimer,QRect, Qt
from PIL import Image
from decord import VideoReader
from decord import cpu,gpu
import ctypes
import numpy as np
from qlabel_modify import draw_cross as myLabel
from bezier_curve_generator import *
from linear_curve_generator import *
from cross_point import point_base
from PIL import Image
import cv2
# import scipy.misc
# import threading
import inspect
import ctypes
from threading import Semaphore,Thread
import threed as td

semaphore = Semaphore(1)
button_semaphore = Semaphore(1)
video_chunk = Semaphore(1)
redraw_semaphore = Semaphore(1)

video_chunk_allocator=[]
chunk_urgent_request=0
loadded=0
duration_time=0
file_dir=''
running=True

class feature_map(object):
    def __init__(self, term_crit,track_window,roi_hist):
        self.term_crit=term_crit
        self.track_window=track_window
        self.roi_hist=roi_hist

def video_loader():
    print('running')
    while running:
        if video_chunk.acquire():
            print('get')
            global chunk_urgent_request,loadded
            print(file_dir)
            if file_dir!='':
                print('test')
                print(len(video_chunk_allocator))
                if chunk_urgent_request>len(video_chunk_allocator)-1:
                    print('true')
                    if loadded==len(video_chunk_allocator):
                        pass
                    else:
                        pass
                    # looking for which chunk is not loadded
                
                else:
                    print('access')
                    print(duration_time)
                    print(chunk_urgent_request)
                    print('--------------')
                    if chunk_urgent_request*10+9>duration_time:
                        end=duration_time
                    else:
                        end=chunk_urgent_request*10+9
                    print('*********')
                    print(chunk_urgent_request*10)
                    print(end)
                    clip = VideoFileClip(file_dir).subclip(chunk_urgent_request*10,end)
                    clip.write_videofile("tmp/"+str(chunk_urgent_request)+file_dir[-4:])
                    video_chunk_allocator[chunk_urgent_request]='ready'
                    # global loadded,chunk_urgent_request
                    chunk_urgent_request+=1
                    loadded=loadded+1
            video_chunk.release()
    
def movingAverage(curve, radius): 
	window_size = 2 * radius + 1
	# Define the filter 
	f = np.ones(window_size)/window_size 
	# Add padding to the boundaries 
	curve_pad = np.lib.pad(curve, (radius, radius), 'edge') 
	# Apply convolution 
	curve_smoothed = np.convolve(curve_pad, f, mode='same') 
	# Remove padding 
	curve_smoothed = curve_smoothed[radius:-radius]
	# return smoothed curve
	return curve_smoothed 

def smooth(trajectory): 
	smoothed_trajectory = np.copy(trajectory) 
	# print('smooth')
	# print(smoothed_trajectory)
	# Filter the x, y and angle curves
	for i in range(3):
		smoothed_trajectory[i] = movingAverage(trajectory[i], radius=50)
 
	return smoothed_trajectory

def fixBorder(frame):
    s = frame.shape
    # Scale the image 4% without moving the center
    T = cv2.getRotationMatrix2D((s[1]/2, s[0]/2), 0, 1.04)
    frame = cv2.warpAffine(frame, T, (s[1], s[0]))
    return frame

class Main(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.play_icon=QIcon('icon/play.png')
        self.pause_icon=QIcon('icon/pause.png')
        self.setupUi(self)
        self.init_button_slot()
        self.init_variable()
        print(self.label_width)
        print(self.label_height)
        # t2=Thread(target=self.store_manual_cross_pos)
        # t2.start()

    def init_variable(self):
        self.command_verify=False
        self.timer_camera = QTimer()
        self.timer_camera.timeout.connect(self.play_video)
        self.video_load_flag=False
        self.scaleFactor=1
        self.label_width=self.label.width()
        self.label_height=self.label.height()
        self.play_speed=0
        self.counter=0
        self.playing=False
        self.stop_flag=True
        self.file_name=None
        # self.interpolation=''
        self.cross_point_storage={}
        self.cross_auto_calculate={}
        self.video_meta=[]
        self.total_frame_num=0
        self.frame_indicator=0
        self.interpolation_method='Off'
        self.video_stabilize='Off'
        self.red=None
        self.green=None
        self.black=None
        self.blue=None
        self.red_list=[]
        self.red_list_indicator=[]
        self.green_list=[]
        self.green_list_indicator=[]
        self.black_list=[]
        self.black_list_indicator=[]
        self.blue_list=[]
        self.blue_list_indicator=[]
        # self.red_feature_flag=0
        # self.blue_feature_flag=0
        # self.black_feature_flag=0
        # self.green_feature_flag=0
        self.red_calculate_x=[]
        self.red_calculate_y=[]
        self.red_calculate_key=[]

        self.green_calculate_x=[]
        self.green_calculate_y=[]
        self.green_calculate_key=[]

        self.blue_calculate_x=[]
        self.blue_calculate_y=[]
        self.blue_calculate_key=[]

        self.black_calculate_x=[]
        self.black_calculate_y=[]
        self.black_calculate_key=[]
    
    def init_button_slot(self):
        self.label.setScaledContents (True)
        self.radioButton_3.setChecked(True)
        self.radioButton_6.setChecked(True)
        self.pushButton.clicked.connect(self.load_video)
        self.pushButton_3.clicked.connect(self.play_stop)
        self.comboBox.currentIndexChanged.connect(self.draw)

        # self.comboBox.currentTextChanged.connect(self.restore)
        self.horizontalSlider.sliderPressed.connect(self.slide_stop)
        self.horizontalSlider.sliderReleased.connect(self.slide_release)
        self.pushButton_7.clicked.connect(self.print_axis)
        self.pushButton_6.clicked.connect(self.speed_up)
        self.pushButton_5.clicked.connect(self.slow_down)

        self.pushButton_2.clicked.connect(self.zoom_in)
        self.pushButton_4.clicked.connect(self.zoom_out)
        self.scrollArea.horizontalScrollBar().valueChanged.connect(self.horizontal_value)
        self.scrollArea.verticalScrollBar().valueChanged.connect(self.vertical_value)

        self.pushButton_3.setIcon(self.play_icon)
        self.radioButton.toggled.connect(self.onClicked_interpolation)
        self.radioButton_2.toggled.connect(self.onClicked_interpolation)
        self.radioButton_3.toggled.connect(self.onClicked_video_stabilize)
        self.radioButton_4.toggled.connect(self.onClicked_video_stabilize)
        self.radioButton_6.toggled.connect(self.onClicked_video_stabilize)

    def print_axis(self):
        red_cross_x=[]
        red_cross_y=[]
        red_cross_key=[]
        # red_calculate_x=[]
        # red_calculate_y=[]
        # red_calculate_key=[]

        green_cross_x=[]
        green_cross_y=[]
        green_cross_key=[]
        # green_calculate_x=[]
        # green_calculate_y=[]
        # green_calculate_key=[]

        blue_cross_x=[]
        blue_cross_y=[]
        blue_cross_key=[]
        # blue_calculate_x=[]
        # blue_calculate_y=[]
        # blue_calculate_key=[]

        black_cross_x=[]
        black_cross_y=[]
        black_cross_key=[]
        # black_calculate_x=[]
        # black_calculate_y=[]
        # black_calculate_key=[]
        for key,targets in self.cross_point_storage.items():
            try:
                for color,target in targets.items():
                    if target.color=='red':
                        red_cross_x.append(target.x)
                        red_cross_y.append(target.y)
                        red_cross_key.append(key)
                    elif target.color=='green':
                        green_cross_x.append(target.x)
                        green_cross_y.append(target.y)
                        green_cross_key.append(key)
                    elif target.color=='blue':
                        blue_cross_x.append(target.x)
                        blue_cross_y.append(target.y)
                        blue_cross_key.append(key)
                    elif target.color=='black':
                        black_cross_x.append(target.x)
                        black_cross_y.append(target.y)
                        black_cross_key.append(key)
            except:
                pass

        
        if self.video_load_flag==True:
            td.call_3d_graph(red_cross_x,red_cross_y,red_cross_key,self.red_calculate_x,self.red_calculate_y,self.red_calculate_key)
            td.call_3d_graph(green_cross_x,green_cross_y,green_cross_key,self.green_calculate_x,self.green_calculate_y,self.green_calculate_key)
            td.call_3d_graph(blue_cross_x,blue_cross_y,blue_cross_key,self.blue_calculate_x,self.blue_calculate_y,self.blue_calculate_key)
            td.call_3d_graph(black_cross_x,black_cross_y,black_cross_key,self.black_calculate_x,self.black_calculate_y,self.black_calculate_key)
    
    def horizontal_value(self,value):
        print(self.label_width)
        print(value)
        # print(self.scrollArea.horizontalScrollBar())
        print(self.scrollArea.horizontalScrollBar().singleStep())
        print(self.scrollArea.horizontalScrollBar().maximum())
        print(self.scrollArea.horizontalScrollBar().width())
        self.redraw()
        # print(self.scrollArea.horizontalScrollBar())
        print('---------------------')

    def vertical_value(self,value):
        print('vertical')
        print(self.label_height)
        print(value)
        # print(self.scrollArea.horizontalScrollBar())
        print(self.scrollArea.verticalScrollBar().singleStep())
        print(self.scrollArea.verticalScrollBar().maximum())
        print(self.scrollArea.verticalScrollBar().height())
        self.redraw()
        # print(self.scrollArea.horizontalScrollBar())
        print('---------------------')
    
    def re_calculate_cross_point(self,point_pos_x,point_pos_y,flag):
        if self.scaleFactor>1:
            if flag=='store':
                pos_x,pos_y=(point_pos_x+self.scrollArea.horizontalScrollBar().value())/self.scaleFactor,(point_pos_y+self.scrollArea.verticalScrollBar().value())/self.scaleFactor
                return pos_x,pos_y
            elif flag=='retrive':
                pos_x,pos_y=(point_pos_x*self.scaleFactor-self.scrollArea.horizontalScrollBar().value()+22),(point_pos_y*self.scaleFactor-self.scrollArea.verticalScrollBar().value()+22)
                return pos_x,pos_y
            else:
                pass
        return point_pos_x,point_pos_y
    
    def redraw(self):
        if self.radioButton_3.isChecked()==True:
            # print('redraw set true')
            self.cross_tmp_storage=self.cross_point_storage
        else:
            # print('redraw set false')
            self.cross_tmp_storage=self.cross_auto_calculate
        # print('+++++++++++++++++++++++++++++')
        # print(self.cross_tmp_storage)
        # print('+++++++++++++++++++++++++++++')
        if self.cross_tmp_storage.get(self.frame_indicator)!=None:
            # print('redrawing')
            layout = self.verticalLayout_2.layout()
            # 获取 Layout 上的控件
            widget = layout.itemAt(0).widget()
            painterInstance =QPainter(widget.pixmap())
            # painterInstance.setPen(QPen(Qt.red,2,Qt.SolidLine))
            targets=self.cross_tmp_storage.get(self.frame_indicator)

            track_windows=[]
            for key,target in targets.items():
                hsv = cv2.cvtColor(self.video_meta[self.frame_indicator].asnumpy(), cv2.COLOR_BGR2HSV)
                track_windows.clear()
                if target.color== 'red':
                    painterInstance.setPen(QPen(Qt.red,4,Qt.SolidLine))
                    if(len(self.red_list_indicator)!=0):
                        determine_flag=0
                        for indicator in self.red_list_indicator:
                            if(self.frame_indicator<indicator):
                                break
                            else:
                                determine_flag+=1
                        
                        red=self.red_list[determine_flag]
                        dst = cv2.calcBackProject([hsv],[0],red.roi_hist,[0,180],1)
                        ret, track_window = cv2.meanShift(dst, red.track_window, red.term_crit)
                        track_windows.append(track_window)
                elif target.color == 'green':
                    painterInstance.setPen(QPen(Qt.green,4,Qt.SolidLine))
                    if(len(self.green_list_indicator)!=0):
                        determine_flag=0
                        for indicator in self.green_list_indicator:
                            if(self.frame_indicator<indicator):
                                break
                            else:
                                determine_flag+=1

                        green=self.green_list[determine_flag]
                        dst = cv2.calcBackProject([hsv],[0],green.roi_hist,[0,180],1)
                        ret, track_window = cv2.meanShift(dst, green.track_window, green.term_crit)
                        track_windows.append(track_window)
                elif target.color == 'black':
                    painterInstance.setPen(QPen(Qt.black,4,Qt.SolidLine))
                    if(len(self.black_list_indicator)!=0):
                        determine_flag=0
                        for indicator in self.black_list_indicator:
                            if(self.frame_indicator<indicator):
                                break
                            else:
                                determine_flag+=1

                        black=self.black_list[determine_flag]
                        dst = cv2.calcBackProject([hsv],[0],black.roi_hist,[0,180],1)
                        ret, track_window = cv2.meanShift(dst, black.track_window, black.term_crit)
                        track_windows.append(track_window)
                elif target.color == 'blue':
                    painterInstance.setPen(QPen(Qt.blue,4,Qt.SolidLine))
                    if(len(self.blue_list_indicator)!=0):
                        determine_flag=0
                        for indicator in self.blue_list_indicator:
                            if(self.frame_indicator<indicator):
                                break
                            else:
                                determine_flag+=1
                        
                        blue=self.blue_list[determine_flag]
                        dst = cv2.calcBackProject([hsv],[0],blue.roi_hist,[0,180],1)
                        ret, track_window = cv2.meanShift(dst, blue.track_window, blue.term_crit)
                        track_windows.append(track_window)
                else:
                    painterInstance.setPen(QPen(Qt.red,4,Qt.CustomDashLine)) 
                # print(rect)
                x0,y0=target.x,target.y
                min_pos=-1
                for index,track_window in enumerate(track_windows):
                    x,y,x1,y1=track_window
                    x2,y2=x+10,y+10
                    if(x2-x0<=15 and y2-y0<=15):
                        min_pos=index
                if(min_pos!=-1):
                    # print('find new pos before')
                    # print(x0,y0)
                    x,y,w,h=track_windows[min_pos]
                    x0,y0=x0+10,y0+10

                if target.color=='red':
                    self.red_calculate_x.append(x0)
                    self.red_calculate_y.append(y0)
                    self.red_calculate_key.append(self.frame_indicator)

                elif target.color=='green':
                    self.green_calculate_x.append(x0)
                    self.green_calculate_y.append(y0)
                    self.green_calculate_key.append(self.frame_indicator)

                elif target.color=='blue':
                    self.blue_calculate_x.append(x0)
                    self.blue_calculate_y.append(y0)
                    self.blue_calculate_key.append(self.frame_indicator)

                elif target.color=='black':
                    self.black_calculate_x.append(x0)
                    self.black_calculate_y.append(y0)
                    self.black_calculate_key.append(self.frame_indicator)
                # print('add x0,y0')
                # print(x0,y0)
                if(self.radioButton_6.isChecked()==True):
                    x0,y0=self.re_calculate_cross_point(x0,y0,'retrive')
                    painterInstance.drawLine(x0,y0,x0+10,y0+10)
                    painterInstance.drawLine(x0,y0,x0-10,y0+10)
                    painterInstance.drawLine(x0,y0,x0+10,y0-10)
                    painterInstance.drawLine(x0,y0,x0-10,y0-10)
                # print('---------')
            painterInstance.end()
            widget.update()
    
    def store_manual_cross_pos(self):
        frame_storage={}
        try:
            point=point_base(self.red.x0,self.red.y0,'red','manual')
            point_dict={'red':point}
            if point.x!=0:
                frame_storage.update(point_dict)
                feature_obj=feature_map(self.red.term_crit, self.red.track_window, self.red.roi_hist)
                # tmp={self.frame_indicator:feature_obj}
                self.red_list_indicator.append(self.frame_indicator)
                self.red_list.append(feature_obj)
        except:
            pass

        try:
            point=point_base(self.blue.x0,self.blue.y0,'blue','manual')
            point_dict={'blue':point}
            if point.x!=0:
                frame_storage.update(point_dict)
                feature_obj=feature_map(self.blue.term_crit, self.blue.track_window, self.blue.roi_hist)
                # tmp={self.frame_indicator:feature_obj}
                self.blue_list_indicator.append(self.frame_indicator)
                self.blue_list.append(feature_obj)
        except:
            pass

        try:
            point=point_base(self.green.x0,self.green.y0,'green','manual')
            point_dict={'green':point}
            if point.x!=0:
                frame_storage.update(point_dict)
                feature_obj=feature_map(self.green.term_crit, self.green.track_window, self.green.roi_hist)
                # tmp={self.frame_indicator:feature_obj}
                self.green_list_indicator.append(self.frame_indicator)
                self.green_list.append(feature_obj)
        except:
            pass

        try:
            point=point_base(self.black.x0,self.black.y0,'black','manual')
            point_dict={'black':point}
            if point.x!=0:
                frame_storage.update(point_dict)
                feature_obj=feature_map(self.black.term_crit, self.black.track_window, self.black.roi_hist)
                # tmp={self.frame_indicator:feature_obj}
                self.black_list_indicator.append(self.frame_indicator)
                self.black_list.append(feature_obj)
        except:
            pass

        if len(frame_storage)!=0:
            frame={self.frame_indicator:frame_storage}
            self.cross_point_storage.update(frame)
            self.cross_point_storage=dict(sorted(self.cross_point_storage.items(), key=operator.itemgetter(0)))
            # print(self.cross_point_storage)
            if self.interpolation_method!='Off':
                self.calculate_point()
    
    def get_centre_point(self):
        # for key,all_cross in self.cross_auto_calculate.items():
        all_cross=self.cross_auto_calculate.get(self.frame_indicator)
        if all_cross!=None:
            cross_num=len(all_cross)
            if cross_num>1:
                x_axis_sum=0
                y_axis_sum=0
                w=all_cross[sorted(all_cross,key=lambda x: all_cross[x].x,reverse=True)[0]].x-all_cross[sorted(all_cross,key=lambda x: all_cross[x].x)[0]].x
                h=all_cross[sorted(all_cross,key=lambda x: all_cross[x].y,reverse=True)[0]].y-all_cross[sorted(all_cross,key=lambda x: all_cross[x].y)[0]].y
                
                for color,cross in all_cross.items():
                    # print(cross)
                    x_axis_sum=cross.x+x_axis_sum
                    y_axis_sum=cross.y+y_axis_sum

                centre_x=int(x_axis_sum/cross_num)
                centre_y=int(y_axis_sum/cross_num)
                return (centre_x,centre_y,w,h)
            else:
                for color,cross in all_cross.items():
                    centre_x=cross.x
                    centre_y=cross.y
                
                return (centre_x,centre_y,50,50)

    def calculate_point(self):
        print('running')
        print(self.interpolation_method)
        self.cross_auto_calculate.clear()
        red_cross_storage=[]
        green_cross_storage=[]
        black_cross_storage=[]
        blue_cross_storage=[]
        red_cross_step=[]
        green_cross_step=[]
        black_cross_step=[]
        blue_cross_step=[]
        for key,target in self.cross_point_storage.items():
            try:
                frame=target['red']
                x0,y0=self.re_calculate_cross_point(frame.x,frame.y,'store')
                point=[x0,y0]
                red_cross_storage.append(point)
                red_cross_step.append(key)
            except:
                pass
                
            try:
                frame=target['green']
                x0,y0=self.re_calculate_cross_point(frame.x,frame.y,'store')
                point=[x0,y0]
                green_cross_storage.append(point)
                green_cross_step.append(key)
            except:
                pass

            try:
                frame=target['black']
                x0,y0=self.re_calculate_cross_point(frame.x,frame.y,'store')
                point=[x0,y0]
                black_cross_storage.append(point)
                black_cross_step.append(key)
            except:
                pass

            try:
                frame=target['blue']
                x0,y0=self.re_calculate_cross_point(frame.x,frame.y,'store')
                point=[x0,y0]
                blue_cross_storage.append(point)
                blue_cross_step.append(key)
            except:
                pass
        
        try:
            if(self.interpolation_method=='Bezier Curve'):
                red_cross_result=get_coordinates(red_cross_storage,max(red_cross_step)-min(red_cross_step)-1)
            else:
                red_cross_result=get_coordinate(red_cross_storage,max(red_cross_step)-min(red_cross_step)-1,red_cross_step)
        except:
            red_cross_result=[]
            red_cross_step.append(0)
        
        try:
            if(self.interpolation_method=='Bezier Curve'):
                green_cross_result=get_coordinates(green_cross_storage,max(green_cross_step)-min(green_cross_step)-1)
            else:
                green_cross_result=get_coordinate(green_cross_storage,max(green_cross_step)-min(green_cross_step)-1,green_cross_step)
            # green_cross_result=get_coordinates(green_cross_storage,max(green_cross_step)-min(green_cross_step)-1)
        except:
            green_cross_result=[]
            green_cross_step.append(0)
        
        try:
            if(self.interpolation_method=='Bezier Curve'):
                black_cross_result=get_coordinates(black_cross_storage,max(black_cross_step)-min(black_cross_step)-1)
            else:
                black_cross_result=get_coordinate(black_cross_storage,max(black_cross_step)-min(black_cross_step)-1,black_cross_step)
            # black_cross_result=get_coordinates(black_cross_storage,max(black_cross_step)-min(black_cross_step)-1)
        except:
            black_cross_result=[]
            black_cross_step.append(0)
        
        try:
            if(self.interpolation_method=='Bezier Curve'):
                blue_cross_result=get_coordinates(blue_cross_storage,max(blue_cross_step)-min(blue_cross_step)-1)
            else:
                blue_cross_result=get_coordinate(blue_cross_storage,max(blue_cross_step)-min(blue_cross_step)-1,blue_cross_step)
            # blue_cross_result=get_coordinates(blue_cross_storage,max(blue_cross_step)-min(blue_cross_step)-1)
        except:
            blue_cross_result=[]
            blue_cross_step.append(0)
        

        counter=min(red_cross_step)
        if counter!=0 and len(red_cross_step)>1:
            for red_cross in red_cross_result:
                point=point_base(red_cross[0],red_cross[1],'red','auto')
                tmp={'red':point}
                tmp_2={counter:tmp}
                # print('determine')
                # print(self.cross_auto_calculate.get(counter))
                if self.cross_auto_calculate.get(counter)==None:
                    self.cross_auto_calculate.update(tmp_2)
                else:
                    tmp_storage=self.cross_auto_calculate[counter]
                    tmp_storage['red']=point
                    self.cross_auto_calculate.update(tmp_storage)
                counter+=1
                # print(self.cross_auto_calculate)
            # print(self.cross_auto_calculate)
            # print('++++++++++++++++++++++++++++++++++++++++++')
        
        counter=min(green_cross_step)
        if counter!=0 and len(green_cross_step)>1:
            for green_cross in green_cross_result:
                point=point_base(green_cross[0],green_cross[1],'green','auto')
                tmp={'green':point}
                tmp_2={counter:tmp}
                if self.cross_auto_calculate.get(counter)==None:
                    self.cross_auto_calculate.update(tmp_2)
                else:
                    tmp_storage=self.cross_auto_calculate[counter]
                    tmp_storage['green']=point
                    self.cross_auto_calculate.update(tmp_storage)
                counter+=1
            print(self.cross_auto_calculate)
            print('++++++++++++++++++++++++++++++++++++++++++')
        
        counter=min(black_cross_step)
        if counter!=0 and len(black_cross_step)>1:
            for black_cross in black_cross_result:
                point=point_base(black_cross[0],black_cross[1],'black','auto')
                tmp={'black':point}
                tmp_2={counter:tmp}
                if self.cross_auto_calculate.get(counter)==None:
                    self.cross_auto_calculate.update(tmp_2)
                else:
                    tmp_storage=self.cross_auto_calculate[counter]
                    tmp_storage['black']=point
                    self.cross_auto_calculate.update(tmp_storage)
                counter+=1
            print(self.cross_auto_calculate)
            print('++++++++++++++++++++++++++++++++++++++++++')
        
        counter=min(blue_cross_step)
        if counter!=0 and len(blue_cross_step)>1:
            for blue_cross in blue_cross_result:
                point=point_base(blue_cross[0],blue_cross[1],'blue','auto')
                tmp={'blue':point}
                tmp_2={counter:tmp}
                if self.cross_auto_calculate.get(counter)==None:
                    self.cross_auto_calculate.update(tmp_2)
                else:
                    tmp_storage=self.cross_auto_calculate[counter]
                    tmp_storage['blue']=point
                    self.cross_auto_calculate.update(tmp_storage)
                counter+=1
            print(self.cross_auto_calculate)
            print('++++++++++++++++++++++++++++++++++++++++++')
        

    def get_rid_off_cross(self):
        try:
            self.red.x0=0
            self.red.y0=0
            self.red.close()
        except:
            pass

        try:
            self.blue.x0=0
            self.blue.y0=0
            self.blue.close()
        except:
            pass

        try:
            self.green.x0=0
            self.green.y0=0
            self.green.close()
        except:
            pass

        try:
            self.black.x0=0
            self.black.y0=0
            self.black.close()
        except:
            pass
  
    def draw(self):
        if len(self.video_meta)==0:
            QMessageBox.critical(self, "warning", "you have to import a video first")
            
            # print(self.scrollArea.horizontalScrollBar().value())
            # print(self.scrollArea.horizontalScrollBar().singleStep())
            
        else:
            if semaphore.acquire():
                self.video_stop()
                if self.comboBox.currentText() == 'red':
                    self.red = myLabel(self.label)
                    self.red.frame_data=self.video_meta[self.frame_indicator]
                    self.red.setGeometry(QRect(10, 10, 1000, 600))
                    self.red.color =  self.comboBox.currentText()
                    self.red.setCursor(Qt.CrossCursor)
                    self.red.show()
                elif self.comboBox.currentText() == 'green':
                    self.green = myLabel(self.label)
                    self.green.frame_data=self.video_meta[self.frame_indicator]
                    self.green.setGeometry(QRect(10, 10, 1000, 600))
                    self.green.color =  self.comboBox.currentText()
                    self.green.setCursor(Qt.CrossCursor)
                    self.green.show()
                elif self.comboBox.currentText() == 'black':
                    self.black = myLabel(self.label)
                    self.black.frame_data=self.video_meta[self.frame_indicator]
                    self.black.setGeometry(QRect(10, 10, 1000, 600))
                    self.black.color =  self.comboBox.currentText()
                    self.black.setCursor(Qt.CrossCursor)
                    self.black.show()            
                elif self.comboBox.currentText() == 'blue':
                    self.blue = myLabel(self.label)
                    self.blue.frame_data=self.video_meta[self.frame_indicator]
                    self.blue.setGeometry(QRect(10, 10, 1000, 600))
                    self.blue.color =  self.comboBox.currentText()
                    self.blue.setCursor(Qt.CrossCursor)
                    self.blue.show()      
                else:
                    pass
                # self.calculate_point()
                semaphore.release()
                self.comboBox.setCurrentIndex(0)

    def zoom_in(self):
        print('zoom in')
        # if self.scaleFactor<1:
        
        # self.scaleFactor+=0.01
        print(self.scrollArea.horizontalScrollBar().value())
        print(self.scrollArea.horizontalScrollBar().minimum())
        print(self.scrollArea.horizontalScrollBar().maximum())
        if len(self.video_meta)!=0:
            self.scaleFactor=self.scaleFactor*1.25
            self.label_width=self.label.width()*1.25
            self.label_height=self.label.height()*1.25
            self.display(self.video_meta[self.frame_indicator])
            # self.scrollArea.horizontalScrollBar().setPageStep(855)
            # self.scrollArea.horizontalScrollBar().setMaximum(int(self.label_width)-200)
            # self.scrollArea.verticalScrollBar().setRange(0,self.label_height)
            print(self.label_width)
            print('*****')
            print(self.scrollArea.horizontalScrollBar().maximum())
            
            print(self.scrollArea.horizontalScrollBar().pageStep())
            print(self.scrollArea.horizontalScrollBar().singleStep())
            print('*****')
            # self.scrollArea.horizontalScrollBar().setValue(self.label_width)
            # self.scrollArea.verticalScrollBar().setValue(self.label_height)

        # print(self.scaleFactor)
        # if self.stop_flag==False:
        #     self.command_verify=True
        #     self.display(self.video_meta[self.frame_indicator])
    
    def zoom_out(self):
        print('zoom out')
        # if self.scaleFactor>1:
        #     self.scaleFactor=0.9
        # self.scaleFactor-=0.01
        # print(self.scaleFactor)
        # if self.stop_flag==False:
        #     self.command_verify=True
        #     self.display(self.video_meta[self.frame_indicator])
        if len(self.video_meta)!=0:
            self.scaleFactor=self.scaleFactor*0.8
            if self.scaleFactor<1:
                self.scaleFactor=1
                self.label_width=self.label.width()*1.0
                self.label_height=self.label.height()*1.0
            else:
                self.label_width=self.label.width()*0.8
                self.label_height=self.label.height()*0.8
            self.display(self.video_meta[self.frame_indicator])
            # self.scrollArea.horizontalScrollBar().setRange(0,self.label_width)
            # self.scrollArea.verticalScrollBar().setRange(0,self.label_height)
            # self.scrollArea.horizontalScrollBar().setValue(self.label_width)
            # self.scrollArea.verticalScrollBar().setValue(self.label_height)
    
    def speed_up(self):
        self.play_speed+=1
        if self.play_speed>=0:
            self.counter=0
    
    def slow_down(self):
        self.play_speed-=1
    
    def scale_image(self):
        print('scale')
        print(self.scaleFactor)
        self.label.resize(self.scaleFactor * self.label.pixmap().size())
    
    def load_video(self):
        if video_chunk.acquire():
            print(self.video_load_flag)
            # 暂停播放
            
            directory, _ = QFileDialog.getOpenFileName(self,"choose file",
                    "./",
                    "Media Files(*.mp4)")
            if directory=='':
                return
            print('66666666666666666666666666666666666')
            print(directory)
            global file_dir,duration_time
            file_dir=directory
            clip_meta = VideoFileClip(directory)
            duration_time=clip_meta.reader.duration
            chunk_num=duration_time/10
            self.cross_point_storage.clear()
            self.cross_auto_calculate.clear()
            if duration_time%10!=0:
                chunk_num+=1
            for i in range(int(chunk_num)):
                video_chunk_allocator.append('request')
            # t1=Thread(target=video_loader)
            # t1.start()

            # self.video_cut(clip_meta,directory,0,frame_num)
            self.video_meta= VideoReader(directory, ctx=cpu(0))
            print(type(self.video_meta[0]))
            print(sys.getsizeof(self.video_meta))
            self.horizontalSlider.setMaximum(len(self.video_meta)-1)
            print(len(self.video_meta))
            self.total_frame_num=len(self.video_meta)
            self.file_name=directory.split('/')[-1]
            self.playing=False
            self.frame_indicator=0
            self.video_load_flag=True
            self.horizontalSlider.setValue(0)
            self.pushButton_3.setIcon(self.play_icon)
            self.display(self.video_meta[0].asnumpy())
            video_chunk.release()
    
    def video_cut(self,meta_clip,file_name,start,length,chunk_indicator=-1,flag=False):
        end=0
        print(length)
        if flag==True:
            return
        if start+10>=length-1:
            end=length-1-start
            flag=True
        else:
            end=start+10
        clip = meta_clip.subclip(start,end)
        clip.write_videofile("tmp/tmp"+str(chunk_indicator+1)+file_name[-4:])
        self.video_cut(meta_clip,file_name,end+1,length,chunk_indicator+1,flag)
    
    def video_stop(self):
        # self.stop_flag= not self.stop_flag
        self.timer_camera.stop()   # 停止计时器
        self.pushButton_3.setIcon(self.play_icon)
    
    def video_resume(self):
        # self.stop_flag= not self.stop_flag
        self.timer_camera.start(50)
        self.pushButton_3.setIcon(self.pause_icon)
    
    def play_stop(self):
        if len(self.video_meta)!=0:
            if self.playing==False:
                self.playing=True
                self.pushButton_3.setIcon(self.pause_icon)
                self.timer_camera.start(50)  
                # self.timer_camera.timeout.connect(self.play_video)
            else:
                self.stop_flag= not self.stop_flag
                if self.stop_flag==False:
                    self.video_stop()
                else:
                    self.video_resume()
    
    def play_video(self):
        if semaphore.acquire():
            # print(len(self.video_meta))
            if self.playing==True:
            
                if len(self.video_meta)!=0:
                    self.store_manual_cross_pos()

                    self.get_rid_off_cross()

                    self.frame_indicator_determine()


                    frame_meta=self.video_meta[self.frame_indicator].asnumpy()
                    if(self.video_stabilize=='On'):
                        if self.frame_indicator>0:
                            centre_x,centre_y,w,h=self.get_centre_point()
                            start_point_x=centre_x-int(w/2)
                            start_point_y=centre_y-int(h/2)
                            frame_meta=self.video_meta[self.frame_indicator].asnumpy()[start_point_y:start_point_y+h,start_point_x:start_point_x+w,:]
                            prev_meta=self.video_meta[self.frame_indicator-1].asnumpy()[start_point_y:start_point_y+h,start_point_x:start_point_x+w,:]
                            im = Image.fromarray(frame_meta)
                            im.save("frame_meta.jpeg")
                            im = Image.fromarray(prev_meta)
                            im.save("prev_meta.jpeg")
                            print('prev_meta')
                            print(prev_meta)
                            prev_gray = cv2.cvtColor(prev_meta, cv2.COLOR_BGR2GRAY)
                            curr_gray = cv2.cvtColor(frame_meta, cv2.COLOR_BGR2GRAY)
                            prev_pts = cv2.goodFeaturesToTrack(prev_gray, maxCorners=200, qualityLevel=0.01, minDistance=30, blockSize=3)
                            curr_pts, status, err = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, prev_pts, None)
                            idx = np.where(status==1)[0]
                            prev_pts = prev_pts[idx]
                            curr_pts = curr_pts[idx]
                            assert prev_pts.shape == curr_pts.shape 


                            # fullAffine= FAlse will set the degree of freedom to only 5 i.e translation, rotation and scaling
                            # try fullAffine = True
                            m, inliers = cv2.estimateAffinePartial2D(prev_pts, curr_pts)

                            dx = m[0,2]
                            dy = m[1,2]

                            # Extract rotation angle
                            da = np.arctan2(m[1,0], m[0,0])
                            transforms=[dx,dy,da]
                            trajectory = np.cumsum(transforms, axis=0)
                            smoothed_trajectory = smooth(trajectory)
                            difference = smoothed_trajectory - trajectory
                            transforms_smooth = transforms + difference 
                            dx = transforms_smooth[0]
                            dy = transforms_smooth[1]
                            da = transforms_smooth[2]

                            # Reconstruct transformation matrix accordingly to new values
                            m = np.zeros((2,3), np.float32)
                            m[0,0] = np.cos(da)
                            m[0,1] = -np.sin(da)
                            m[1,0] = np.sin(da)
                            m[1,1] = np.cos(da)
                            m[0,2] = dx
                            m[1,2] = dy

                            # Apply affine wrapping to the given frame
                            height, width, bytesPerComponent = frame_meta.shape
                            frame_stabilized = cv2.warpAffine(frame_meta, m, (width,height))

                            # Fix border artifacts
                            frame_stabilized = fixBorder(frame_stabilized) 

                            # Write the frame to the file
                            # frame_out = cv2.hconcat([frame_stabilized])
                            frame_meta=frame_stabilized
                            im = Image.fromarray(frame_meta)
                            im.save("your_file.jpeg")
                    # redraw_semaphore.acquire()
                    self.display(frame_meta) 
                    # redraw_semaphore.release()

                    # redraw_semaphore.acquire()
                    self.redraw()
                    # redraw_semaphore.release()
                    
                    # self.frame_indicator=int((self.frame_indicator+1)%(self.total_frame_num-1))
                    self.horizontalSlider.setValue(self.frame_indicator)

                    # print(self.frame_indicator)
                    if self.frame_indicator==self.total_frame_num-2:
                        self.playing=False
                        self.video_load_flag=False
                        self.play_speed=0
                        self.counter=0
                        # print('----------')
                        self.video_stop()
            semaphore.release()
    
    def frame_indicator_determine(self):
        
        if self.play_speed==0:
            self.frame_indicator=int((self.frame_indicator+1)%(self.total_frame_num-1))
        elif self.play_speed>1:
            # self.frame_indicator=self.frame_indicator+self.play_speed
            tmp_pos=self.frame_indicator+self.play_speed
            if tmp_pos>=self.total_frame_num-1:
                self.frame_indicator=self.total_frame_num-2
                # self.video_stop()
            else:
                self.frame_indicator=tmp_pos
        else:
            tmp_speed=abs(self.play_speed)
            self.counter=int((self.counter+1)%tmp_speed)
            if self.counter==0:
                self.frame_indicator+=1
        
        if self.frame_indicator==self.total_frame_num-1:
            self.frame_indicator=self.total_frame_num-2
  
    def display(self,frame_meta):
        
        frame_m=frame_meta

        height, width, bytesPerComponent = frame_m.shape
        
        bytesPerLine = bytesPerComponent * width
        frame=frame_m.data
        # q_image = QImage(frame.data,  width, height, bytesPerLine, 
        #                     QImage.Format_RGB888).scaled(self.label.width()*self.scaleFactor, self.label.height()*self.scaleFactor)
        rcount=ctypes.c_long.from_address(id(frame)).value
        q_image = QImage(frame,  width, height, bytesPerLine, 
                            QImage.Format_RGB888).scaled(self.label_width,self.label_height)
        ctypes.c_long.from_address(id(frame)).value=1
        # print(self.label.width())
        # print(self.label.height())
        # print(self.label_width)
        # print(self.label_height)
        # print('-----------------')
        
        layout = self.verticalLayout_2.layout()
        # print(layout.itemAt(0).widget())
        # 获取 Layout 上的控件
        widget = layout.itemAt(0).widget()

        if(self.video_stabilize=='On'):
            try:
                # im = Image.fromarray(frame_m)
                # im.save("tmp.png")
                
                # img3 = cv2.imdecode(np.fromfile('tmp.png',dtype=np.uint8),-1)
                pass
                # centre_x,centre_y,w,h=self.get_centre_point()
                # start_point_x=centre_x-int(w/2)
                # start_point_y=centre_y-int(h/2)
                # windows=QRect(start_point_x, start_point_y, w, h)
                
                # # q_image = QImage(frame, w, h, bytesPerLine, 
                # #             QImage.Format_RGB888).scaled(self.label_width,self.label_height)
                # widget.setPixmap(QPixmap.fromImage(q_image).copy(windows))
                widget.setPixmap(QPixmap.fromImage(q_image))
            except:
                pass
        else:
            widget.setPixmap(QPixmap.fromImage(q_image))
        # objgraph.show_most_common_types(limit=10)
        # print('----------')
        # self.scale_image()

    def slide_stop(self):
        print('slide')
        self.store_manual_cross_pos()
        self.get_rid_off_cross()
        self.video_stop()
        # value=self.horizontalSlider.value()
        # print(value)
        # self.video_stop()
        # self.frame_indicator=value
        # self.video_resume()
    
    def slide_release(self):
        value=self.horizontalSlider.value()
        self.frame_indicator=value
        frame_meta=self.video_meta[self.frame_indicator].asnumpy()

        self.display(frame_meta) 

        self.redraw()
        
        # self.frame_indicator=int((self.frame_indicator+1)%(self.total_frame_num-1))
        self.horizontalSlider.setValue(self.frame_indicator)
        print(value)
        
        # self.video_resume()
    
    def onClicked_video_stabilize(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            print(radioBtn.text())
            self.video_stabilize=radioBtn.text()
            
    def onClicked_interpolation(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            print(radioBtn.text())
            self.interpolation_method=radioBtn.text()
            if(radioBtn.text()=='Linear'):
                self.calculate_point()
                self.interpolation_method='Linear'
            elif(radioBtn.text()=='Bezier Curve'):
                self.calculate_point()
                self.interpolation_method='Bezier Curve'
            else:
                self.interpolation_method='Off'
        
        # print('setting argument')
        # print(self.interpolation_method)
            
            

def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)

def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Main()
    form.show()
    # t1=Thread(target=video_loader)
    # stop_thread(t1)
    # print(app.exec_())
    if(app.exec_()==0):
        if(file_dir):
            # stop_thread(t1)
            pass
        sys.exit(0)
    # sys.exit(0)