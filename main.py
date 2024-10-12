import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt
from modules.shared import stylesheet, bind_open_video_fn
from modules.monitor import Monitor
from modules.video_select import VideoListWidget
from pathlib import Path
app = QApplication(sys.argv)
app.setStyleSheet(stylesheet)


class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.video_list_widget = None
        self.setWindowTitle("Video Player")
        self.resize(990, 600)

        loading_text = QLabel("Loading...")
        self.setCentralWidget(loading_text)
        self.show()

        video_list_widget = VideoListWidget("./videos")
        self.setCentralWidget(video_list_widget)
        self.setWindowTitle("选择视频文件")

        self.halt_close_event = False
        self.monitor: Monitor = None
        def open_video_fn(video_path: Path):
            self.monitor = Monitor(video_path)
            self.setCentralWidget(self.monitor)
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.monitor.label_list_dock)
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.monitor.labeling_dock)
            self.setWindowTitle("播放视频 | 标注")
            self.halt_close_event = True
            
        bind_open_video_fn(open_video_fn)

    def closeEvent(self, event):
        if self.halt_close_event:
            self.removeDockWidget(self.monitor.label_list_dock)
            self.removeDockWidget(self.monitor.labeling_dock)
            self.monitor.close()
            video_list_widget = VideoListWidget("./videos")
            self.setCentralWidget(video_list_widget)
            self.setWindowTitle("选择视频文件")
            event.ignore()
            self.halt_close_event = False
        else:
            event.accept()

if __name__ == "__main__":
    window = MainWindow()
    sys.exit(app.exec())
