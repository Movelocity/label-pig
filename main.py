import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QVBoxLayout, QPushButton, QSlider, 
    QWidget, QHBoxLayout, QLineEdit, QBoxLayout, QLabel
)
from video_player import VideoPlayer
from label_dialog import ImageLabeling
import cv2

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

class PlayState:
    def __init__(self):
        self.slider = None
        self.time_input = None
        self.seek_video_fn: function = None
        self.frame_rate = 1
        self.max_frame = 2
    def update_position(self, frame_position:int, frame_rate):
        if self.slider is not None:
            self.slider.setValue(frame_position)
        if self.time_input is not None:
            minute_float = frame_position / frame_rate
            minute = int(minute_float / 60)
            second = int(minute_float % 60)
            self.time_input.setText(f"{minute:02d}:{second:02d}")

    def set_max_frame(self, max_frame):
        print("set slider max: ", max_frame)
        if self.slider is not None:
            self.slider.setMaximum(max_frame)  # 视频总帧数
        self.max_frame = max_frame

    def seek_video_by_slider(self):
        frame_position = self.slider.value()
        print("seek to: ", frame_position)
        if self.seek_video_fn is not None:
            self.seek_video_fn(frame_position)
        
    def seek_video_by_time(self):
        time_str = self.time_input.text()
        print('time: ', time_str)
        if not time_str: return

        if ":" in time_str:
            minute, second = map(int, time_str.split(":"))
            frame_position = (minute * 60 + second) * self.frame_rate
            if frame_position > self.max_frame: return
            if self.seek_video_fn is not None:
                self.seek_video_fn(frame_position)

class MainWidget(QWidget):
    def __init__(self, video_path):
        super().__init__()
        self.play_state = PlayState()
        # 创建视频播放器组件
        self.video_player = VideoPlayer(video_path, self.play_state)

        # 布局设置
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_player)
        self.init_controls_ui(main_layout)
        self.init_labeling_ui(main_layout)
        self.setLayout(main_layout)
        # self.label_current_frame()

    def init_controls_ui(self, main_layout:QBoxLayout):
        # 创建播放/停止按钮
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_play)

        # 创建拖动条
        self.play_state.slider = QSlider(Qt.Orientation.Horizontal)
        self.play_state.slider.setRange(0, self.play_state.max_frame)  # 假设视频长度为1000个单位
        self.play_state.slider.sliderPressed.connect(self.pause_video)
        self.play_state.slider.sliderReleased.connect(self.play_state.seek_video_by_slider)

        # 调节时间轴的文本输入框
        self.play_state.time_input = QLineEdit("00:00")
        self.play_state.time_input.setReadOnly(False)
        self.play_state.time_input.setMaximumWidth(80)
        self.play_state.time_input.returnPressed.connect(self.play_state.seek_video_by_time)

        control_layout = QHBoxLayout()
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.play_state.slider)
        control_layout.addWidget(self.play_state.time_input)
        main_layout.addLayout(control_layout)

    def init_labeling_ui(self, main_layout:QBoxLayout):
        auto_label_hint = QLabel('自动标注：')
        self.labeling_prompt = QLineEdit()
        self.labeling_prompt.setPlaceholderText('可指定多种物体,以 . 分隔: cat . dog . bird')
        self.labeling_prompt.setText('pig')
        self.auto_label_btn = QPushButton('自动标注')
        self.auto_label_btn.clicked.connect(self.label_current_frame)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(auto_label_hint)
        controls_layout.addWidget(self.labeling_prompt)
        controls_layout.addWidget(self.auto_label_btn)

        main_layout.addLayout(controls_layout)

    def play_video(self):
        self.video_player.play()
        self.play_button.setText("Stop")

    def pause_video(self):
        self.video_player.stop()
        self.play_button.setText("Play")

    def toggle_play(self):
        if self.video_player.is_playing:
            self.pause_video()
        else:
            self.play_video()

    def label_current_frame(self):
        image = self.video_player.current_frame
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        caption = self.labeling_prompt.text()
        self.currentLabeling = ImageLabeling(image=image, caption=caption)
        self.currentLabeling.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(stylesheet)

    # 视频文件路径
    video_path = "hunting_hog.mp4"

    player_widget = MainWidget(video_path)
    player_widget.setWindowTitle("Video Player")
    player_widget.resize(800, 600)
    player_widget.show()

    sys.exit(app.exec())