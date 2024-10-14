import cv2
# from functools import partial
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QVBoxLayout, QPushButton, QSlider,
    QWidget, QHBoxLayout, QLineEdit, QBoxLayout, 
)

from typing import List
from .label_manager import Label, LabelManager
from .video_player import VideoPlayer, PlayState
from .label_ui import ImageLabeling, LabelingDock, LabelListWidget, plot_annotations
from pathlib import Path


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
        self.labeling_dock = LabelingDock(self.label_current_frame)

        self.label_manager = LabelManager(video_path)
        self.label_list_dock: LabelListWidget = LabelListWidget(
            self.label_manager, 
            jump_to_timestamp=self.jump_to_timestamp,
            to_next_frame=self.video_player.next_frame
        )

        extra_layout.addLayout(main_layout)
        # extra_layout.addWidget(self.label_list_widget)

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

    def label_current_frame(self, caption):
        self.pause_video()
        image = self.video_player.current_frame
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # caption = self.labeling_prompt.text()

        def emit_labels_fn(labels: List[Label]):
            self.label_manager.add_labels(timestamp=self.play_state.get_curr_time(), labels=labels)
            self.label_list_dock.update_ui()
            # print(f"{self.play_state.time_text} | {[str(label) for label in labels]}")
        self.currentLabeling = ImageLabeling(image=image, caption=caption, emit_labels_fn=emit_labels_fn)
        self.currentLabeling.show()
    
    def jump_to_timestamp(self, timestamp):
        self.play_state.seek_video_by_time(timestamp)
        frame = self.video_player.current_frame
        plot = plot_annotations(frame, self.label_manager.get_label_as_list(timestamp))
        self.video_player.set_frame_data(plot)

    def close(self):
        self.video_player.release()
