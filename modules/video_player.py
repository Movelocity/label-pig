import cv2
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QSlider, QLineEdit
import numpy as np

class PlayState:
    def __init__(self):
        self.slider: QSlider = None
        self.time_input: QLineEdit = None
        self.seek_video_fn: function = None
        self.frame_rate = 1
        self.max_frame = 2
        self.time_text: str = "00:00"

    def update_position(self, frame_position:int, frame_rate):
        if self.slider is not None:
            self.slider.setValue(frame_position)
        if self.time_input is not None:
            minute_float = frame_position / frame_rate
            minute = int(minute_float / 60)
            second = int(minute_float % 60)
            self.time_text = f"{minute:02d}:{second:02d}"
            self.time_input.setText(self.time_text)

    def set_max_frame(self, max_frame):
        print("detected frames:", max_frame)
        if self.slider is not None:
            self.slider.setMaximum(max_frame)  # 视频总帧数
        self.max_frame = max_frame

    def seek_video_by_slider(self):
        frame_position = self.slider.value()
        print("seek to: ", frame_position)
        if self.seek_video_fn is not None:
            self.seek_video_fn(frame_position)
        
    def seek_video_by_time_widget(self):
        time_str = self.time_input.text()
        print('time: ', time_str)
        if not time_str: return

        if ":" in time_str:
            minute, second = map(int, time_str.split(":"))
            frame_position = (minute * 60 + second) * self.frame_rate
            if frame_position > self.max_frame: return
            if self.seek_video_fn is not None:
                self.seek_video_fn(frame_position)
    
    def seek_video_by_time(self, timestamp): 
        print('time: ', timestamp)
        if not timestamp: return

        if ":" in timestamp:
            minute, second = map(int, timestamp.split(":"))
            frame_position = (minute * 60 + second) * self.frame_rate
            if frame_position > self.max_frame: return
            if self.seek_video_fn is not None:
                self.seek_video_fn(frame_position)

            self.time_input.setText(timestamp)

class VideoPlayer(QGraphicsView):
    def __init__(self, video_path, play_state):
        super().__init__()
        self.play_state: PlayState = play_state
        self.frame_rate = 30  # 框架慢的因素,其实1s不足以刷新30帧,但你确实可以看到所有帧
        self.play_state.frame_rate = self.frame_rate
        # 创建场景和图片项目
        self.scene: QGraphicsScene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        
        # 创建定时器用于刷新帧
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)

        # 创建控制变量
        self.is_playing = False

        self.current_frame = None

        # 打开视频文件
        self.cap = None 
        def seek_video(frame_position):
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_position)
            self.next_frame()
        self.play_state.seek_video_fn = seek_video
        self.load_video(video_path)

    def load_video(self, video_path):
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            print("无法打开视频: "+video_path)
            return False
        self.play_state.set_max_frame(int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)))
        self.timer.start(self.frame_rate)
        self.timer.stop()
        self.next_frame()
        return True

    def play(self):
        if not self.is_playing:
            self.timer.start(self.frame_rate)  # 设置刷新频率为每30毫秒（约33帧每秒）
            self.is_playing = True

    def stop(self):
        if self.is_playing:
            self.timer.stop()
            self.is_playing = False

    def display_frame(self, frame):
        # frame 应该直接从 ret, frame = self.cap.read() 得到
        # 将帧从BGR格式转换为RGB格式
        frame: np.ndarray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.current_frame = frame
        self.pixmap_item.setPixmap(QPixmap.fromImage(image))

    def next_frame(self):
        ret, frame = self.cap.read()

        if ret:
            # 获取原始帧的宽和高
            original_height, original_width = frame.shape[:2]

            # 计算新的高度，以保持宽高比例
            new_width = 800
            new_height = int((new_width / original_width) * original_height)

            # 调整帧的大小
            resized_frame = cv2.resize(frame, (new_width, new_height))
            self.display_frame(resized_frame)

            frame_position = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.play_state.update_position(frame_position, self.frame_rate)
        else:
            self.stop()  # 视频播放完毕，停止定时器

    def closeEvent(self, event):
        # 关闭视频文件
        self.cap.release()
        event.accept()

    def release(self):
        self.cap.release()