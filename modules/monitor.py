import cv2
# from functools import partial
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QVBoxLayout, QPushButton, QSlider,
    QWidget, QHBoxLayout, QLineEdit, QBoxLayout, QTextEdit, QDockWidget, QListWidget, QListWidgetItem
)
from PyQt6.QtGui import QCursor
from typing import List
from .label_manager import Label, LabelManager
from .video_player import VideoPlayer, PlayState
from .label_dialog import ImageLabeling
from pathlib import Path
from .shared import get_style

class LabelListWidget(QDockWidget):
    def __init__(self, label_manager: LabelManager, jump_to_timestamp: callable):
        super().__init__()
        self.label_manager = label_manager
        self.jump_to_timestamp = jump_to_timestamp
        self.label_list = self.label_manager.time_points
        
        # Create a QListWidget to hold the labels
        self.list_widget = QListWidget()
        self.setWidget(self.list_widget)
        self.setMaximumWidth(140)
        # Optionally set a title for the DockWidget
        self.setWindowTitle("时间轴标签列表")

        self.update_ui()

        # Connect item clicked signal
        self.list_widget.itemClicked.connect(self._jump_to_timestamp)

    def _jump_to_timestamp(self, item: QListWidgetItem):
        # Call the jump function with the timestamp from the clicked item
        timestamp = item.text()
        self.jump_to_timestamp(timestamp)

    def add_label(self, label: Label):
        self.label_list.append(label)
        self.update_ui()

    def update_ui(self):
        # Clear the existing items
        self.list_widget.clear()

        # Add each timestamp as an item in the QListWidget
        for timestamp in self.label_list:
            item = QListWidgetItem(timestamp)
            self.list_widget.addItem(item)

class LabelingDock(QDockWidget):
    def __init__(self, label_current_frame: callable):
        super().__init__()
        self.setWindowTitle('标注工具')
        # 创建一个 QWidget 作为 dock 的主内容
        dock_content = QWidget()

        # 初始布局为水平布局
        controls_layout = QVBoxLayout(dock_content)

        # 创建控件
        # auto_label_hint = QLabel('自动标注：')
        labeling_prompt = QTextEdit()
        labeling_prompt.setPlaceholderText('可指定多种物体,以 . 分隔: cat . dog . bird')
        labeling_prompt.setText('pig')
        auto_label_btn = QPushButton('自动标注')
        auto_label_btn.setStyleSheet(get_style('QPushButton', 'bg: #06b6d3; height: 2em; font-weight:bold', 'bg: #21d2ed;'))
        auto_label_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        def auto_label():
            prompt = labeling_prompt.toPlainText()
            self.label_current_frame(prompt)

        self.label_current_frame = label_current_frame
        auto_label_btn.clicked.connect(auto_label)

        # controls_layout.addWidget(auto_label_hint)
        controls_layout.addWidget(labeling_prompt)
        controls_layout.addWidget(auto_label_btn)

        # 设置 dock 的内容
        self.setWidget(dock_content)

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
        self.label_list_dock: LabelListWidget = LabelListWidget(self.label_manager, jump_to_timestamp=self.jump_to_timestamp)

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
        image = self.video_player.current_frame
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # caption = self.labeling_prompt.text()

        def emit_labels_fn(labels: List[Label]):
            self.label_manager.add_labels(timestamp=self.play_state.time_text, labels=labels)
            self.label_list_dock.update_ui()
            # print(f"{self.play_state.time_text} | {[str(label) for label in labels]}")
        self.currentLabeling = ImageLabeling(image=image, caption=caption, emit_labels_fn=emit_labels_fn)
        self.currentLabeling.show()
    
    def jump_to_timestamp(self, timestamp):
        self.play_state.seek_video_by_time(timestamp)

    def close(self):
        self.video_player.release()
