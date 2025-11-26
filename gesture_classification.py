import cv2
import mediapipe as mp
import math
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os

def vector_2d_angle(v1,v2):
    '''
        求解二维向量的角度,针对非TOF摄像头
    '''
    v1_x=v1[0]
    v1_y=v1[1]
    v2_x=v2[0]
    v2_y=v2[1]
    try:
        angle_= math.degrees(math.acos((v1_x*v2_x+v1_y*v2_y)/(((v1_x**2+v1_y**2)**0.5)*((v2_x**2+v2_y**2)**0.5))))
    except:
        angle_ =65535.
    if angle_ > 180.:
        angle_ = 65535.
    return angle_
def hand_angle(hand_):
    '''
        获取对应手相关向量的二维角度,根据角度确定手势
    '''
    angle_list = []
    #---------------------------- thumb 大拇指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[2][0])),(int(hand_[0][1])-int(hand_[2][1]))),
        ((int(hand_[3][0])- int(hand_[4][0])),(int(hand_[3][1])- int(hand_[4][1])))
        )
    QApplication.processEvents()
    ui.printf('大拇指角度为：' + str(angle_))
    QApplication.processEvents()
    angle_list.append(angle_)
    #---------------------------- index 食指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])-int(hand_[6][0])),(int(hand_[0][1])- int(hand_[6][1]))),
        ((int(hand_[7][0])- int(hand_[8][0])),(int(hand_[7][1])- int(hand_[8][1])))
        )
    QApplication.processEvents()
    ui.printf('食指角度为：' + str(angle_))
    QApplication.processEvents()
    angle_list.append(angle_)
    #---------------------------- middle 中指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[10][0])),(int(hand_[0][1])- int(hand_[10][1]))),
        ((int(hand_[11][0])- int(hand_[12][0])),(int(hand_[11][1])- int(hand_[12][1])))
        )
    QApplication.processEvents()
    ui.printf('中指角度为：' + str(angle_))
    QApplication.processEvents()
    angle_list.append(angle_)
    #---------------------------- ring 无名指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[14][0])),(int(hand_[0][1])- int(hand_[14][1]))),
        ((int(hand_[15][0])- int(hand_[16][0])),(int(hand_[15][1])- int(hand_[16][1])))
        )
    QApplication.processEvents()
    ui.printf('无名指角度为：' + str(angle_))
    QApplication.processEvents()
    angle_list.append(angle_)
    #---------------------------- pink 小拇指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[18][0])),(int(hand_[0][1])- int(hand_[18][1]))),
        ((int(hand_[19][0])- int(hand_[20][0])),(int(hand_[19][1])- int(hand_[20][1])))
        )
    QApplication.processEvents()
    ui.printf('小拇指角度为：' + str(angle_))
    QApplication.processEvents()
    angle_list.append(angle_)
    return angle_list

def h_gesture(angle_list):
    '''
        # 二维约束的方法定义手势
        # fist five gun love one six three thumbup yeah
    '''
    thr_angle = 65.
    thr_angle_thumb = 53.
    thr_angle_s = 49.
    gesture_str = None
    if 65535. not in angle_list:
        if (angle_list[0]>thr_angle_thumb) and (angle_list[1]>thr_angle) and (angle_list[2]>thr_angle) and (angle_list[3]>thr_angle) and (angle_list[4]>thr_angle):
            gesture_str = "one"
        elif (angle_list[0]<thr_angle_s) and (angle_list[1]<thr_angle_s) and (angle_list[2]<thr_angle_s) and (angle_list[3]<thr_angle_s) and (angle_list[4]<thr_angle_s):
            gesture_str = "five"
        elif (angle_list[0]>5)  and (angle_list[1]<thr_angle_s) and (angle_list[2]>thr_angle) and (angle_list[3]>thr_angle) and (angle_list[4]>thr_angle):
            gesture_str = "one"
        elif (angle_list[0]<thr_angle_s)  and (angle_list[1]>thr_angle) and (angle_list[2]>thr_angle) and (angle_list[3]>thr_angle) and (angle_list[4]<thr_angle_s):
            gesture_str = "six"
        elif (angle_list[0]>thr_angle_thumb)  and (angle_list[1]<thr_angle_s) and (angle_list[2]<thr_angle_s) and (angle_list[3]<thr_angle_s) and (angle_list[4]>thr_angle):
            gesture_str = "three"
        elif (angle_list[0]>thr_angle_thumb)  and (angle_list[1]<thr_angle_s) and (angle_list[2]<thr_angle_s) and (angle_list[3]>thr_angle) and (angle_list[4]>thr_angle):
            gesture_str = "two"
    return gesture_str

class Thread_1(QThread):  # 线程1
    log_signal = pyqtSignal(str)
    frame_signal = pyqtSignal(object)

    def __init__(self, info1):
        super().__init__()
        self.info1 = info1
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.75,
                min_tracking_confidence=0.75)

        try:
            cap_source = int(self.info1)
        except ValueError:
            cap_source = self.info1

        cap = cv2.VideoCapture(cap_source)

        if not cap.isOpened():
            self.log_signal.emit(f"错误：无法打开视频源 '{self.info1}'")
            return

        while self._is_running and cap.isOpened():
            ret,frame = cap.read()
            if not ret:
                self.log_signal.emit("视频处理完成或摄像头断开。")
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame= cv2.flip(frame,1)
            results = hands.process(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    hand_local = []
                    for i in range(21):
                        x = hand_landmarks.landmark[i].x*frame.shape[1]
                        y = hand_landmarks.landmark[i].y*frame.shape[0]
                        hand_local.append((x,y))
                    if hand_local:
                        # 在这个线程中计算角度，但不更新UI
                        angle_list = self.calculate_hand_angle(hand_local)
                        gesture_str = h_gesture(angle_list)
                        self.log_signal.emit('手势识别结果为： ' + str(gesture_str))
                        cv2.putText(frame, gesture_str if gesture_str else "...", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 3)

            self.frame_signal.emit(frame)
            # self.msleep(30) # 控制帧率，减轻CPU负担

        cap.release()
        hands.close()
        self.log_signal.emit("识别线程已停止。")

    def calculate_hand_angle(self, hand_):
        angle_list = []
        # 大拇指角度
        angle_ = vector_2d_angle(
            ((int(hand_[0][0])- int(hand_[2][0])),(int(hand_[0][1])-int(hand_[2][1]))),
            ((int(hand_[3][0])- int(hand_[4][0])),(int(hand_[3][1])- int(hand_[4][1])))
            )
        angle_list.append(angle_)
        # 食指角度
        angle_ = vector_2d_angle(
            ((int(hand_[0][0])-int(hand_[6][0])),(int(hand_[0][1])- int(hand_[6][1]))),
            ((int(hand_[7][0])- int(hand_[8][0])),(int(hand_[7][1])- int(hand_[8][1])))
            )
        angle_list.append(angle_)
        # 中指角度
        angle_ = vector_2d_angle(
            ((int(hand_[0][0])- int(hand_[10][0])),(int(hand_[0][1])- int(hand_[10][1]))),
            ((int(hand_[11][0])- int(hand_[12][0])),(int(hand_[11][1])- int(hand_[12][1])))
            )
        angle_list.append(angle_)
        # 无名指角度
        angle_ = vector_2d_angle(
            ((int(hand_[0][0])- int(hand_[14][0])),(int(hand_[0][1])- int(hand_[14][1]))),
            ((int(hand_[15][0])- int(hand_[16][0])),(int(hand_[15][1])- int(hand_[16][1])))
            )
        angle_list.append(angle_)
        # 小拇指角度
        angle_ = vector_2d_angle(
            ((int(hand_[0][0])- int(hand_[18][0])),(int(hand_[0][1])- int(hand_[18][1]))),
            ((int(hand_[19][0])- int(hand_[20][0])),(int(hand_[19][1])- int(hand_[20][1])))
            )
        angle_list.append(angle_)
        return angle_list

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1113, 848)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(320, 5, 460, 60))
        self.textBrowser.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.textBrowser.setObjectName("textBrowser")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(230, 155, 191, 51))
        self.pushButton.setStyleSheet("background-color: rgb(0,255,0);\n"
"font: 20pt \"3ds\";")
        self.pushButton.setObjectName("pushButton")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(100, 70, 901, 61))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setStyleSheet("font: 12pt \"3ds\";\n"
"background-color: rgb(253, 255, 211);")
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.textEdit = QtWidgets.QTextEdit(self.layoutWidget)
        self.textEdit.setObjectName("textEdit")
        self.horizontalLayout.addWidget(self.textEdit)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(20, 228, 261, 16))
        self.label_3.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"font: 12pt \"3ds\";")
        self.label_3.setObjectName("label_3")
        self.textBrowser_2 = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser_2.setGeometry(QtCore.QRect(20, 250, 261, 561))
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(710, 155, 191, 51))
        self.pushButton_3.setStyleSheet("background-color: rgb(255, 0, 0);\n"
"font: 20pt \"3ds\";")
        self.pushButton_3.setObjectName("pushButton_3")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(290, 230, 801, 16))
        self.label_5.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"font: 12pt \"3ds\";")
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(290, 260, 781, 501))
        self.label_6.setText("")
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(720, 260, 371, 301))
        self.label_7.setText("")
        self.label_7.setObjectName("label_7")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1113, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.pushButton.clicked.connect(self.click_1)
        self.pushButton_3.clicked.connect(self.handleCalc3)

        self.thread_1 = None
        MainWindow.closeEvent = self.closeEvent

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.textBrowser.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:26pt;\">手势识别系统</span></p></body></html>"))
        self.pushButton.setText(_translate("MainWindow", "开始识别"))
        self.label.setText(_translate("MainWindow", "输入路径："))
        self.label_3.setText(_translate("MainWindow", "            识别日志"))
        self.pushButton_3.setText(_translate("MainWindow", "停止识别"))
        self.label_5.setText(_translate("MainWindow", "                                          识别结果"))

    def handleCalc3(self):
        if self.thread_1 and self.thread_1.isRunning():
            self.thread_1.stop()
            self.thread_1.wait() # 等待线程结束
        self.printf("识别已停止。")


    def printf(self,text):
        self.textBrowser_2.append(text)
        self.cursor = self.textBrowser_2.textCursor()
        self.textBrowser_2.moveCursor(self.cursor.End)
        # QtWidgets.QApplication.processEvents() # 不再需要

    def showimg(self,img):
        global video, size

        # 确保写入的帧尺寸正确
        h, w, ch = img.shape
        if (w, h) != size:
            try:
                frame_to_write = cv2.resize(img, size)
                video.write(frame_to_write)
            except Exception as e:
                self.printf(f"视频帧写入/缩放失败: {e}")
        else:
            video.write(img)

        img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        _image = QtGui.QImage(img2.data, img2.shape[1], img2.shape[0], img2.shape[1] * 3,
                              QtGui.QImage.Format_RGB888)

        # 调整图像以适应标签大小
        scaled_pixmap = QPixmap.fromImage(_image).scaled(self.label_6.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_6.setPixmap(scaled_pixmap)


    def click_1(self):
        if self.thread_1 and self.thread_1.isRunning():
            self.printf("错误：一个识别任务正在运行。请先停止。")
            return

        info1 = self.textEdit.toPlainText().strip()
        if not info1:
            self.printf("请输入视频路径或摄像头ID（例如 0）。")
            return

        self.printf(f"正在启动识别，源: {info1}")
        self.thread_1 = Thread_1(info1)
        self.thread_1.log_signal.connect(self.printf)
        self.thread_1.frame_signal.connect(self.showimg)
        self.thread_1.finished.connect(lambda: self.pushButton.setEnabled(True))
        self.pushButton.setEnabled(False)
        self.thread_1.start()

    def closeEvent(self, event):
        self.handleCalc3()
        global video
        if video:
            video.release()
        event.accept()

if __name__ == "__main__":
    size = (1918, 1046)
    video = cv2.VideoWriter("./Video.avi", cv2.VideoWriter_fourcc('I', '4', '2', '0'), 30, size)
    app = QtWidgets.QApplication(sys.argv)  # 创建一个QApplication，也就是你要开发的软件app
    MainWindow = QtWidgets.QMainWindow()  # 创建一个QMainWindow，用来装载你需要的各种组件、控件
    ui = Ui_MainWindow()  # ui是Ui_MainWindow()类的实例化对象
    ui.setupUi(MainWindow)  # 执行类中的setupUi方法，方法的参数是第二步中创建的QMainWindow
    MainWindow.show()  # 执行QMainWindow的show()方法，显示这个QMainWindow
    app.exec_()
    video.release() # 确保程序退出时释放video
    sys.exit()
