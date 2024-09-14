import sys
import cv2
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel,
    QSlider, QLineEdit, QPushButton, QTextEdit, 
    QVBoxLayout, QHBoxLayout, QBoxLayout,
    QStyle, QDialog
)
# from api import image_detect_api
from label_dialog import ImageLabeling

stylesheet = """
QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
}
QLineEdit, QTextEdit, QPushButton {
    background-color: #3c3c3c;
    border: 1px solid #5a5a5a;
    border-radius: 5px;
    padding: 5px;
}
QSlider::groove:horizontal {
    border: 1px solid #5a5a5a;
    height: 8px;
    background: #3c3c3c;
}
QSlider::handle:horizontal {
    background: #5a5a5a;
    border: 1px solid #5a5a5a;
    width: 18px;
    margin: -2px 0;
    border-radius: 3px;
}
"""

class ConfigDialog(QDialog):
    def __init__(self, parent, config_items:dict):
        super().__init__(parent)
        self.setWindowTitle("全局参数配置")
        self.setFixedSize(400, 200)

        self.layout : QBoxLayout = QVBoxLayout()

        self.input_widgets = {}

        for item_name, item_body in config_items.items():
            label = QLabel(f"{item_body['label']}:")
            input_widget = QLineEdit()
            input_widget.setText(str(item_body.get('value', '')))
            self.input_widgets[item_name] = input_widget

            row_layout = QHBoxLayout()
            row_layout.addWidget(label)
            row_layout.addWidget(input_widget)
            row_widget = QWidget()
            row_widget.setLayout(row_layout)
            self.layout.addWidget(row_widget)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)

        self.setLayout(self.layout)

    def get_values(self):
        config = {}
        for name, widget in self.input_widgets.items():
            try:
                config[name] = float(widget.text())
            except ValueError:
                config[name] = widget.text()
        return config

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.cap = None
        self.frame_rate = 30
        self.is_paused = False
        self.is_playing = False
        self.subtitles = []
        self.auto_label_text = ''

        self.config_items = {
            'frame_rate': {'label': '帧率(fps)', 'value': 30},
        }

        self.initUI()

    def open_config_dialog(self):
        dialog = ConfigDialog(None, self.config_items)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config_values = dialog.get_values()
            print(config_values)

    def initVideoPlayUI(self, layout:QBoxLayout):
        # 显示图片每一帧，随时间刷新
        self.video_frame = QLabel('Video Frame')
        self.video_frame.setMinimumSize(640, 480)
        self.video_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 视频播放时间轴
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.sliderPressed.connect(self.pause_video)
        self.slider.sliderReleased.connect(self.seek_video)

        # 调节时间轴的文本输入框
        self.time_input = QLineEdit()
        self.time_input.setMaximumWidth(80)
        self.time_input.returnPressed.connect(self.seek_video_by_time)

        # 视频播放按钮
        self.play_button = QPushButton('Play')
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.clicked.connect(self.play_pause_video)

        layout.addWidget(self.video_frame)
        row1 = QHBoxLayout()
        row1.addWidget(self.slider, stretch=2)
        row1.addWidget(self.time_input)
        layout.addLayout(row1)

    def initTextLabelUI(self, layout:QBoxLayout):
        self.auto_label_hint = QLabel('自动标注：')
        self.auto_label_name = QLineEdit()
        self.auto_label_name.setPlaceholderText('cat . dog . bird')
        self.auto_label_name.setText('pig')
        self.auto_label_btn = QPushButton('自动标注')
        self.auto_label_btn.clicked.connect(self.auto_label)
        # # 标注文本输入
        # self.subtitle_input = QTextEdit()
        # self.subtitle_input.setPlaceholderText('Enter subtitle here...')
        # # 保存该帧的标注文本
        # self.save_subtitle_button = QPushButton('保存标注')
        # self.save_subtitle_button.clicked.connect(self.save_subtitle)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.auto_label_hint)
        controls_layout.addWidget(self.auto_label_name)
        controls_layout.addWidget(self.auto_label_btn)

        layout.addLayout(controls_layout)

        # label_layout = QHBoxLayout()
        # label_layout.addWidget(self.subtitle_input)
        # label_layout.addWidget(self.save_subtitle_button)
        # layout.addLayout(label_layout)

    def auto_label(self):
        self.currentLabeling = ImageLabeling(image=self.current_frame, caption=self.auto_label_name.text())
        self.currentLabeling.show()
    def initUI(self):
        # Set the font for the entire application (optional)
        font = QFont("Arial", 10)
        self.setFont(font)

        # 设置样式
        self.setStyleSheet(stylesheet)

        # Create a slider for setting frame rate
        # self.frame_rate_input = QLineEdit(str(self.frame_rate),self)
        # self.frame_rate_input.returnPressed.connect(self.change_frame_rate)

        # Layout
        layout = QVBoxLayout()
        self.initVideoPlayUI(layout)
        self.initTextLabelUI(layout)

        # self.config_btn = QPushButton('配置')
        # self.config_btn.clicked.connect(self.open_config_dialog)
        # layout.addWidget(self.config_btn)

        self.setLayout(layout)
        self.setWindowTitle("Video Player")

    def load_video(self, video_path):
        self.cap = cv2.VideoCapture(video_path)
        self.frame_rate = self.cap.get(cv2.CAP_PROP_FPS)
        self.slider.setMaximum(int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))) # 视频总帧数
        # self.frame_rate_input.setText(str(self.frame_rate))
        self.nextFrameSlot()

    def play_pause_video(self):
        if self.is_playing:
            self.pause_video()
        else:
            self.play_video()

    def play_video(self):
        if not self.is_playing and self.cap is not None:
            self.is_playing = True
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            self.play_button.setText('Pause')
            self.timer.start(int(1000 / self.frame_rate))

    def pause_video(self):
        if self.is_playing:
            self.is_paused = True
            self.is_playing = False
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.play_button.setText('Play')
            self.timer.stop()

    def nextFrameSlot(self):
        ret, frame = self.cap.read()
        if ret:
            self.display_frame(frame)
            self.slider.setValue(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)))
            self.time_input.setText(f"{self.cap.get(cv2.CAP_PROP_POS_FRAMES) / self.frame_rate:.2f}s")
        else:
            self.timer.stop()

    def seek_video(self):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.slider.value())
        self.nextFrameSlot()

    def seek_video_by_time(self):
        frame_num = int(float(self.time_input.text()) * self.frame_rate)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        self.nextFrameSlot()

    def display_frame(self, frame):
        # QtGUI 使用 RGB 颜色通道顺序
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 获取当前窗口大小
        window_width = self.video_frame.width()
        window_height = self.video_frame.height()
        
        # 缩放幅度
        scale_factor = min(window_width / frame.shape[1], window_height / frame.shape[0], 1024 / frame.shape[1])
        
        # 缩放一帧图片
        frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
        self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame.shape
        bytesPerLine = 3 * width
        qImg = QImage(
            frame.data, width, height, bytesPerLine, 
            QImage.Format.Format_RGB888
        )
        pixmap = QPixmap.fromImage(qImg)
        self.video_frame.setPixmap(pixmap)

    def save_subtitle(self):
        current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        timestamp = current_frame / self.frame_rate
        subtitle_text = self.subtitle_input.toPlainText()
        self.subtitles.append((timestamp, subtitle_text))
        with open('subtitles.txt', 'a') as f:
            f.write(f"{timestamp:.2f}-{subtitle_text}\n")
        self.subtitle_input.clear()

    def set_frame_rate(self, new_frame_rate):
        if self.config_items['frame_rate']['value'] - new_frame_rate > 0.01:
            print('update frame rate: ', self.frame_rate)
            if self.is_playing:
                self.timer.start(int(1000 / self.frame_rate))
            self.config_items['frame_rate']['value'] = new_frame_rate

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.resize(800, 600)
    player.load_video('hunting_hog.mp4')  # Replace with your video path
    player.show()
    sys.exit(app.exec())
