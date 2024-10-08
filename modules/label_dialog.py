import sys
import cv2
import numpy as np
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QBoxLayout, QLineEdit
)
import re

# import asyncio
from . import api as detection_api

def increment_name(input_str):
    # 使用正则表达式匹配 name 或 name+num 模式
    match = re.match(r"^(\D+)(\d*)$", input_str)
    
    if match:
        name = match.group(1)  # 提取name部分
        num = match.group(2)   # 提取num部分

        if num == "":
            num = 1  # 如果没有num部分，将num设为1
        else:
            num = int(num) + 1  # 如果有num部分，则将其自增

        return f"{name}{num}"
    else:
        return f"{name}1"
    

class ImageLabeling(QWidget):
    def __init__(self, image: np.ndarray, caption: str, emit_labels_fn: callable):
        super().__init__()
        self.image = image
        self.caption = caption
        self.emit_labels_fn = emit_labels_fn
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

    def load_image(self):  # 绘图
        height, width, channel = self.image.shape
        bytes_per_line = 3 * width

        # Clear previous drawings on the image
        image_copy = self.image.copy()

        # Define a list of colors for different boxes
        colors = [
            (230, 100, 0), (0, 177, 177), (0, 0, 222),
            (211, 222, 0), (200, 0, 200), (0, 255, 255)
        ]

        # Calculate font scale based on image size
        font_scale = max(0.5, min(width, height) / 800.0)

        # Draw boxes and labels on the image before displaying it
        for i, box in enumerate(self.annotations):
            cx, cy, w, h = (box[0] * width, box[1] * height, box[2] * width, box[3] * height)
            w_2, h_2 = (w / 2, h / 2)
            color = colors[i % len(colors)]
            cv2.rectangle(image_copy, (int(cx - w_2), int(cy - h_2)), (int(cx + w_2), int(cy + h_2)), color, 2)
            
            # Draw the label text with background
            label_text = box[4] if len(box) > 4 else "Unknown"
            (text_width, text_height), baseline = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)
            text_x = int(cx - w_2)
            text_y = int(cy - h_2) - 6
            padding = 2

            # Draw the background rectangle for text
            cv2.rectangle(image_copy, (text_x, text_y - text_height - padding), 
                        (text_x + text_width + padding * 2, text_y + baseline), color, cv2.FILLED)

            # Draw the text over the background
            cv2.putText(image_copy, label_text, (text_x + padding, text_y - padding), 
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 1)

        q_image = QImage(image_copy.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
        self.image_label.setPixmap(QPixmap.fromImage(q_image))  # Convert to QPixmap
    
    def load_annotations(self):
        # labeling_result = asyncio.run(detection_api.image_detect_api_async(self.image, self.caption))
        labeling_result = detection_api.image_detect_api(self.image, self.caption)
        # labeling_result = {  # 样本
        #     'msg': 'success'
        #     'boxes': [
        #         [0.2300889492034912, 0.43166184425354004, 0.42723730206489563, 0.5608834624290466], 
        #         [0.7489202618598938, 0.45753565430641174, 0.4995116591453552, 0.7285897731781006]
        #     ], 
        #     'logits': [0.5680023431777954, 0.5597519278526306], 
        #     'phrases': ['fruit', 'fruit']
        # }
        if not labeling_result['msg'] == 'success':
            print(labeling_result['msg'])
            return
        label_set = set()
        if 'boxes' in labeling_result:
            self.annotations = labeling_result['boxes']
            for i in range(len(self.annotations)):
                label = labeling_result['phrases'][i]
                label = increment_name(label)
                if label in label_set:
                    label = increment_name(label)
                label_set.add(label)
                self.annotations[i].append(label)  # 默认标签
                
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
            label = self.table.cellWidget(row, 4).text().strip().replace(' ', '_')
            self.annotations[row] = [x, y, width, height] + [label]  # Update annotation with new label
        
        self.load_image()  # Reload image to reflect changes

    def save_annotations(self):
        saved_annotations = []
        for row in range(self.table.rowCount()):
            x = float(self.table.cellWidget(row, 0).text())
            y = float(self.table.cellWidget(row, 1).text())
            width = float(self.table.cellWidget(row, 2).text())
            height = float(self.table.cellWidget(row, 3).text())
            label = self.table.cellWidget(row, 4).text().strip().replace(' ', '_')
            saved_annotations.append((x, y, width, height, label))

        # print("Saved Annotations:", saved_annotations)
        self.emit_labels_fn(saved_annotations)

    def save_and_close(self):
        self.save_annotations()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    image = cv2.imread('pineapple.png')  # Replace with your image path
    dialog = ImageLabeling(image=image, caption="fruit")
    dialog.show()
    sys.exit(app.exec())