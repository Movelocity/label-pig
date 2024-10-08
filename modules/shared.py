# 项目全局变量

open_video_fn: callable = None

def bind_open_video_fn(fn):
    global load_video_fn
    load_video_fn = fn

def get_open_video_fn():
    return load_video_fn

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

QTableView QTableCornerButton::section {
    background: #2b2b2b;
    border: 2px outset #2b2b2b;
}
QTableView QHeaderView::section {
    background: #26312e;
    border: 2px outset #26312e;
}
"""