import sys
import cv2
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QVBoxLayout, QPushButton, QSlider, 
    QWidget, QHBoxLayout, QLineEdit, QBoxLayout, QLabel, QMessageBox
)
from .video_player import VideoPlayer, PlayState
from .label_dialog import ImageLabeling


class Monitor(QWidget):
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

        def emit_labels_fn(labels):
            print(f"{self.play_state.time_text} | {labels}")
        self.currentLabeling = ImageLabeling(image=image, caption=caption, emit_labels_fn=emit_labels_fn)
        self.currentLabeling.show()
    

    def closeEvent(self, event):
        # 阻止关闭事件，并弹出提示框
        
        print('guanbi')
        event.accept()