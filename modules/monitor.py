import cv2
from functools import partial
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QVBoxLayout, QPushButton, QSlider, 
    QWidget, QHBoxLayout, QLineEdit, QBoxLayout, QLabel, QMessageBox
)
from typing import List
from . label_manager import Label, LabelManager
from .video_player import VideoPlayer, PlayState
from .label_dialog import ImageLabeling
from pathlib import Path

class LabelListWidget(QWidget):
    def __init__(self, label_manager: LabelManager, jump_to_timestamp: callable):
        super().__init__()
        self.label_manager = label_manager
        self.jump_to_timestamp = jump_to_timestamp
        self.label_list = self.label_manager.time_points
        self.layout: QBoxLayout = QVBoxLayout()
        self.layout.addWidget(QLabel("标签列表"))
        self.setLayout(self.layout)
        self.load_labels()

    def _jump_to_timestamp(self, timestamp, event):
        self.jump_to_timestamp(timestamp)

    def add_label(self, label: Label):
        self.label_list.append(label)
        # self.update_ui()

    def load_labels(self):
        for timestamp in self.label_list:
            item: QWidget = QLabel(timestamp)
            item.mousePressEvent = partial(self._jump_to_timestamp, timestamp)
            # item: QWidget = QPushButton(timestamp)
            # item.clicked.connect(lambda: self.jump_to_timestamp(timestamp))
            self.layout.addWidget(item)
        self.layout.addStretch()  # 底部留白


class Monitor(QWidget):
    def __init__(self, video_path: Path):
        super().__init__()
        self.play_state = PlayState()

        extra_layout = QHBoxLayout()
        self.setLayout(extra_layout)

        # 创建视频播放器组件
        self.video_player = VideoPlayer(str(video_path), self.play_state)

        # 布局设置
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_player)
        self.init_controls_ui(main_layout)
        self.init_labeling_ui(main_layout)
        # self.setLayout(main_layout)

        self.label_manager = LabelManager(video_path)
        self.label_list_widget = LabelListWidget(self.label_manager, jump_to_timestamp=self.jump_to_timestamp)

        extra_layout.addLayout(main_layout)
        extra_layout.addWidget(self.label_list_widget)

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
        self.play_state.time_input.returnPressed.connect(self.play_state.seek_video_by_time_widget)

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

        def emit_labels_fn(labels: List[Label]):
            self.label_manager.add_labels(timestamp=self.play_state.time_text, labels=labels)
            print(f"{self.play_state.time_text} | {[str(label) for label in labels]}")
        self.currentLabeling = ImageLabeling(image=image, caption=caption, emit_labels_fn=emit_labels_fn)
        self.currentLabeling.show()
    
    def jump_to_timestamp(self, timestamp):
        self.play_state.seek_video_by_time(timestamp)

    def close(self):
        self.video_player.release()
