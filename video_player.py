import cv2
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem

class VideoPlayer(QGraphicsView):
    def __init__(self, video_path, play_state):
        super().__init__()
        self.play_state = play_state
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
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.current_frame = frame
        self.pixmap_item.setPixmap(QPixmap.fromImage(image))

    def next_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.display_frame(frame)
            frame_position = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.play_state.update_position(frame_position, self.frame_rate)
        else:
            self.stop()  # 视频播放完毕，停止定时器

    def closeEvent(self, event):
        # 关闭视频文件
        self.cap.release()
        event.accept()

