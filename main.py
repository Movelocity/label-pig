import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from modules.shared import stylesheet, bind_open_video_fn
from modules.monitor import Monitor
from modules.video_select import VideoListWidget

app = QApplication(sys.argv)
app.setStyleSheet(stylesheet)


class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.video_list_widget = None
        self.setWindowTitle("Video Player")
        self.resize(800, 600)

        loading_text = QLabel("Loading...")
        self.setCentralWidget(loading_text)
        self.show()

        video_list_widget = VideoListWidget("./videos")
        self.setCentralWidget(video_list_widget)

        self.halt_close_event = False

        def open_video_fn(video_path):
            monitor = Monitor(video_path)
            self.setCentralWidget(monitor)
            self.halt_close_event = True
            print('loading video...')
        bind_open_video_fn(open_video_fn)

    def closeEvent(self, event):
        if self.halt_close_event:
            video_list_widget = VideoListWidget("./videos")
            self.setCentralWidget(video_list_widget)
            event.ignore()
            self.halt_close_event = False
        else:
            event.accept()

if __name__ == "__main__":
    window = MainWindow()
    sys.exit(app.exec())