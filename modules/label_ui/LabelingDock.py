from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTextEdit, QDockWidget
)
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import Qt
from ..shared import get_style

class LabelingDock(QDockWidget):
    def __init__(self, label_current_frame: callable):
        super().__init__()
        self.setWindowTitle('标注工具')
        # 创建一个 QWidget 作为 dock 的主内容
        dock_content = QWidget()

        # 初始布局为水平布局
        controls_layout = QVBoxLayout(dock_content)

        # 创建控件
        labeling_prompt = QTextEdit()
        labeling_prompt.setPlaceholderText('可指定多种物体。以 . 分隔:\ncat . dog . bird')
        # labeling_prompt.setText('pig')
        auto_label_btn = QPushButton('新建标注')
        auto_label_btn.setStyleSheet(get_style('QPushButton', 'bg: #06b6d3; height: 2em; font-weight:bold', 'bg: #21d2ed;'))
        auto_label_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        def auto_label():
            prompt = labeling_prompt.toPlainText()
            if prompt == '':
                return
            self.label_current_frame(prompt)

        self.label_current_frame = label_current_frame
        auto_label_btn.clicked.connect(auto_label)

        controls_layout.addWidget(labeling_prompt)
        controls_layout.addWidget(auto_label_btn)

        # 设置 dock 的内容
        self.setWidget(dock_content)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
