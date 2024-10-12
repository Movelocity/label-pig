import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QScrollArea, QLineEdit, QMessageBox, QInputDialog, QPushButton
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QEvent
import cv2  # 需要 OpenCV 生成缩略图
import numpy as np
from . shared import get_open_video_fn
from pathlib import Path


class VideosInfo:
    def __init__(self, video_folder: Path):
        self.video_folder = video_folder
        self.info_file = video_folder / '.cache/info.json'
        self.info_file.parent.mkdir(parents=True, exist_ok=True)
        self.video_info = self.load_info()
        self.scan_videos()

    def load_info(self) -> dict:
        """从 info.json 加载视频信息"""
        if self.info_file.exists():
            with open(self.info_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_info(self) -> None:
        """将视频信息保存到 info.json"""
        with open(self.info_file, 'w', encoding='utf-8') as f:
            json.dump(self.video_info, f, ensure_ascii=False, indent=2)

    def scan_videos(self) -> None:
        """扫描文件夹内的视频文件并提取信息"""
        for video_path in self.video_folder.glob('*'):
            if video_path.suffix in ['.mp4', '.avi', '.mov', '.mkv']:  # 支持的视频格式
                self.prepare_video_info(video_path)
        self.save_info()  # 保存更新的信息

    def prepare_video_info(self, video_path: Path) -> None:
        """获取或更新视频信息"""
        thumbnail_path = video_path.parent / f".cache/{video_path.stem}.jpg"
 
        video_key = video_path.name
        if video_key not in self.video_info:
            cap = cv2.VideoCapture(str(video_path))
            success, frame = cap.read()
            
            if success:
                frame = cv2.resize(frame, (160, 90))  # 缩略图大小 160x90
                cv2.imwrite(str(thumbnail_path), frame)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # RGB
            else:
                frame = np.random.randint(0, 255, (90, 160, 3), np.uint8)
                cv2.imwrite(str(thumbnail_path), frame)

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            duration = frame_count / fps if fps > 0 else 0
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            dimensions = f"{width} x {height}"
            cap.release()

            self.video_info[video_key] = {
                'path': str(video_path),
                'duration': duration,
                'dimensions': dimensions,
                'thumbnail_p': str(thumbnail_path)
            }

            # print(self.video_info[video_key])

    def get_video_info(self, video_key: str) -> dict:
        """获取视频信息"""
        return self.video_info[video_key]

class VideoItem(QWidget):
    def __init__(self, video_path: Path, video_info: dict):
        super().__init__()
        self.video_path: Path = video_path

        self.thumbnail = self.read_thumbnail(video_info['thumbnail_p'])
        self.duration = f"{video_info['duration']:.2f} 秒"
        self.dimensions = video_info['dimensions']
        
        self.layout: QHBoxLayout = QHBoxLayout()

        self.thumbnail_label = QLabel()
        self.thumbnail_label.setPixmap(self.thumbnail)

        # 获取 thumbnail 的高度并设置 thumbnail_label 的高度
        thumbnail_height = self.thumbnail.height()
        self.thumbnail_label.setFixedHeight(int(thumbnail_height * 1.2))
        self.setFixedWidth(int(self.thumbnail.width()*2))
        # 创建一个 QWidget 来包裹 attr_layout
        self.attr_widget = QWidget()
        attr_layout: QVBoxLayout = QVBoxLayout(self.attr_widget)
        
        # 设置 attr_widget 的高度与 thumbnail_label 的高度相同
        self.attr_widget.setFixedHeight(self.thumbnail_label.height())
        self.name_label = QLabel(video_path.name)
        self.name_label.mousePressEvent = self.start_rename
        
        self.duration_label = QLabel(f"时长: {self.duration}")
        self.dimensions_label = QLabel(f"尺寸: {self.dimensions}")

        self.rename_input = QLineEdit()
        self.rename_input.setVisible(False)
        self.rename_input.returnPressed.connect(self.rename_video_from_input)

        def open_file():
            print("open", self.video_path)
            open_video_fn = get_open_video_fn()
            if open_video_fn is not None: 
                open_video_fn(self.video_path)
        self.open_btn = QPushButton("打开")
        self.open_btn.clicked.connect(open_file)

        attr_layout.addWidget(self.name_label)
        attr_layout.addWidget(self.rename_input)
        attr_layout.addWidget(self.duration_label)
        attr_layout.addWidget(self.dimensions_label)
        attr_layout.addWidget(self.open_btn)
        attr_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.layout.addWidget(self.thumbnail_label)
        self.layout.addWidget(self.attr_widget)  # 使用 attr_widget
        self.setLayout(self.layout)

        # 安装事件过滤器
        self.installEventFilter(self)

    def read_thumbnail(self, thumbnail_path):
        frame = frame = cv2.imread(thumbnail_path)
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            q_image = QPixmap.fromImage(image)
            return q_image
        return QPixmap(160, 90)  # 返回空缩略图

    def get_video_dimensions(self):
        # 使用 OpenCV 获取视频尺寸
        cap = cv2.VideoCapture(self.video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        return f"{width} x {height}"

    def start_rename(self, event):
        self.name_label.setVisible(False)
        self.rename_input.setText(self.name_label.text())
        self.rename_input.setVisible(True)
        self.rename_input.setFocus()

    def rename_video_from_input(self):
        new_name = self.rename_input.text()
        if new_name:
            self.rename_video(new_name)

    def rename_video(self, new_name=None):
        if new_name is None:
            new_name, ok = QInputDialog.getText(self, "重命名视频", "新文件名:")
            if not ok or not new_name:
                return
        new_file_path = self.video_path / new_name
        try:
            self.video_path.rename(new_file_path)
            self.video_path = new_file_path
            self.name_label.setText(new_name)
            self.rename_input.setVisible(False)
            self.name_label.setVisible(True)
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
        
    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if self.rename_input.isVisible() and source is not self.rename_input:
                self.rename_input.setVisible(False)
                self.name_label.setVisible(True)
        return super().eventFilter(source, event)


class VideoListWidget(QScrollArea):
    def __init__(self, directory):
        super().__init__()
        self.video_items = []
        self.setWidgetResizable(True)
        self.videos_info = VideosInfo(Path(directory))
        self.container = QWidget()
        self.layout: QVBoxLayout = QVBoxLayout()
        self.container.setLayout(self.layout)
        self.setWidget(self.container)
        
        self.load_videos(directory)

    def load_videos(self, directory):
        for file_name in os.listdir(directory):
            if file_name.endswith(('.mp4', '.avi', '.mov', '.mkv')):  # 支持的视频格式
                video_path = Path(os.path.join(directory, file_name))
                video_item = VideoItem(
                    video_path, 
                    self.videos_info.get_video_info(file_name)
                )
                self.add_video_item(video_item)
        self.layout.addStretch()  # 底部留白
    def add_video_item(self, video_item):
        self.layout.addWidget(video_item)
        self.video_items.append(video_item)


class SelectorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("视频文件浏览器")

        self.video_list_widget = VideoListWidget('./videos')
        self.setCentralWidget(self.video_list_widget)

        self.setup_ui()

    def setup_ui(self):
        self.setGeometry(100, 100, 300, 600)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SelectorWindow()
    window.show()
    sys.exit(app.exec())
