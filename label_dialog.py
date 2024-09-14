import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QBoxLayout,
    QTableWidgetItem, QLineEdit
)
from PyQt6.QtGui import QImage, QPixmap

import asyncio
from api import image_detect_api

class ImageLabeling(QWidget):
    def __init__(self, image: np.ndarray, caption: str):
        super().__init__()
        self.image = image
        self.caption = caption
        self.annotations = []

        self.setWindowTitle("Image Annotation")
        self.setGeometry(100, 100, 800, 600)

        self.layout : QBoxLayout = QVBoxLayout()
        
        # Label to display the image
        self.image_label = QLabel(self)
        
        self.layout.addWidget(self.image_label)
        
        # Table for annotations
        self.table = QTableWidget(self)
        self.layout.addWidget(self.table)

        # Update button
        # self.update_btn = QPushButton("更新", self)
        # self.update_btn.clicked.connect(self.update_annotations)
        # self.layout.addWidget(self.update_btn)
        self.layout4buttons = QHBoxLayout()
        # Refresh button
        self.refresh_btn = QPushButton("刷新", self)
        self.refresh_btn.clicked.connect(self.update_annotations)
        self.layout4buttons.addWidget(self.refresh_btn)

        # Save button
        self.save_button = QPushButton("保存", self)
        self.save_button.clicked.connect(self.save_and_close)
        self.layout4buttons.addWidget(self.save_button)
        self.layout.addLayout(self.layout4buttons)

        self.setLayout(self.layout)

        # Load annotations from API
        self.load_annotations()

    def load_image(self):
        height, width, channel = self.image.shape
        bytes_per_line = 3 * width

        # Clear previous drawings on the image
        image_copy = self.image.copy()

        # Draw boxes and labels on the image before displaying it
        for box in self.annotations:
            cx, cy, w, h = (box[0] * width, box[1] * height, box[2] * width, box[3] * height)
            w_2, h_2 = (w / 2, h / 2)
            cv2.rectangle(image_copy, (int(cx - w_2), int(cy - h_2)), (int(cx + w_2), int(cy + h_2)), (230, 100, 0), 2)
            
            # Draw the label text
            label_text = box[4] if len(box) > 4 else "Unknown"
            cv2.putText(image_copy, label_text, (int(cx - w_2), int(cy - h_2) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        q_image = QImage(image_copy.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
        self.image_label.setPixmap(QPixmap.fromImage(q_image))  # Convert to QPixmap
    
    def load_annotations(self):
        response = asyncio.run(image_detect_api(self.image, self.caption))
        # response = {  # 临时使用测试数据，节省api调用次数
        #     'boxes': [
        #         [0.2300889492034912, 0.43166184425354004, 0.42723730206489563, 0.5608834624290466], 
        #         [0.7489202618598938, 0.45753565430641174, 0.4995116591453552, 0.7285897731781006]
        #     ], 
        #     'logits': [0.5680023431777954, 0.5597519278526306], 
        #     'phrases': ['fruit', 'fruit']
        # }
        if 'boxes' in response:
            self.annotations = response['boxes']
            for i in range(len(self.annotations)):
                self.annotations[i].append(response['phrases'][i])  # 默认标签
            
            self.setup_table()
        self.load_image()

    def setup_table(self):
        self.table.setRowCount(len(self.annotations))
        self.table.setColumnCount(5)  # 4 for coordinates and 1 for label
        self.table.setHorizontalHeaderLabels(['cx', 'cy', 'w', 'h', 'Label'])

        column_widths = [100, 100, 100, 100, 150]
        for i, width in enumerate(column_widths):
            self.table.setColumnWidth(i, width)

        for row_idx, box in enumerate(self.annotations):
            for col_idx in range(4):
                value = f"{box[col_idx]:.3f}"
                item = QLineEdit(value)
                self.table.setCellWidget(row_idx, col_idx, item)

            label_edit = QLineEdit(box[4])  # Default label from annotations
            self.table.setCellWidget(row_idx, 4, label_edit)

    def update_annotations(self):
        # Update annotations based on the table values
        for row in range(self.table.rowCount()):
            x = float(self.table.cellWidget(row, 0).text())
            y = float(self.table.cellWidget(row, 1).text())
            width = float(self.table.cellWidget(row, 2).text())
            height = float(self.table.cellWidget(row, 3).text())
            label = self.table.cellWidget(row, 4).text()
            self.annotations[row] = [x, y, width, height] + [label]  # Update annotation with new label
        
        self.load_image()  # Reload image to reflect changes

    def save_annotations(self):
        saved_annotations = []
        for row in range(self.table.rowCount()):
            x = float(self.table.item(row, 0).text())
            y = float(self.table.item(row, 1).text())
            width = float(self.table.item(row, 2).text())
            height = float(self.table.item(row, 3).text())
            label = self.table.cellWidget(row, 4).text()
            saved_annotations.append((x, y, width, height, label))

        print("Saved Annotations:", saved_annotations)

    def save_and_close(self):
        self.save_annotations()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    image = cv2.imread('pineapple.png')  # Replace with your image path
    dialog = ImageLabeling(image=image, caption="fruit")
    dialog.show()
    sys.exit(app.exec())