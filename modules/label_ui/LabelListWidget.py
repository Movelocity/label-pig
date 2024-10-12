from PyQt6.QtWidgets import (
    QDockWidget, QListWidgetItem, QListWidget, QWidget, QHBoxLayout, QLabel
)
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import Qt
from ..label_manager import Label
from ..label_manager import LabelManager
from ..shared import get_style

class LabelListWidget(QDockWidget):
    def __init__(self, label_manager: LabelManager, jump_to_timestamp: callable, to_next_frame: callable):
        super().__init__()
        self.label_manager = label_manager
        self.jump_to_timestamp = jump_to_timestamp
        self.label_list = self.label_manager.time_points
        self.to_next_frame = to_next_frame
        # Create a QListWidget to hold the labels
        self.list_widget = QListWidget()
        self.setWidget(self.list_widget)
        self.setMaximumWidth(140)
        self.setWindowTitle("时间轴标签列表")

        self.update_ui()

    def add_label(self, label: Label):
        self.label_list.append(label)
        self.update_ui()

    def update_ui(self):
        # Clear the existing items
        self.list_widget.clear()

        # Add each timestamp as an item in the QListWidget
        for timestamp in self.label_list:
            item_widget = QWidget()
            item_widget.setStyleSheet(get_style('QWidget', hover="bg:#1c1917;")+get_style('QLabel', style="bg:transparent;"))
            item_widget.mousePressEvent = lambda _, ts=timestamp: self.jump_to_timestamp(ts)
            layout = QHBoxLayout()

            # 跳转按钮
            info_label = QLabel(timestamp)
            layout.addWidget(info_label)

            layout.addStretch()

            # 删除按钮
            del_button: QLabel = QLabel("X")
            del_button.mousePressEvent = lambda _, ts=timestamp: self.remove_label(ts)
            del_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            layout.addWidget(del_button)

            item_widget.setLayout(layout)

            # Create a QListWidgetItem and set the widget
            list_item = QListWidgetItem(self.list_widget)
            list_item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)

    def remove_label(self, timestamp: str):
        # Remove the label from the list and update the UI
        self.label_manager.remove_label(timestamp)
        self.update_ui()
        self.to_next_frame()
