# 项目全局变量

from pathlib import Path

def get_style(name, style='', hover=''):
    style = style.replace('bg:', 'background-color:')
    hover = hover.replace('bg:', 'background-color:')
    css = ""
    if style != '':
        css += name + " {" + style + "}"
    if hover != '':
        css += name + ":hover {" + hover + "}"
    return css

def open_video_fn(video_path: Path) -> None:
    """
    打开视频文件的函数。

    参数:
        video_path (Path): 视频文件的路径，必须是一个有效的文件路径。

    异常:
        NotImplementedError: 如果没有实现该函数的逻辑。

    使用示例:
        ```
        video_file = Path("path/to/your/video.mp4")
        open_video_fn(video_file)
        ```

    注意: 
        该函数需要被赋值为一个实际的实现。请定义一个新的函数并将其赋值给 open_video_fn。
    """
    raise NotImplementedError(
        "open_video_fn 需要被赋值为一个实现该功能的具体函数。 请定义一个新的函数，并将其赋值给 open_video_fn。"
    )

def bind_open_video_fn(fn):
    global load_video_fn
    load_video_fn = fn

def get_open_video_fn():
    """
    返回一个函数，可以用该函数打开视频文件。

    open_video_fn = get_open_video_fn()
    if open_video_fn is not None: 
        open_video_fn(Path(file_path))
    """
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
  padding: 0 5px;
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
QPushButton {
  height: 18px;
}
QPushButton:pressed {
  background-color: #5a5a5a;
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