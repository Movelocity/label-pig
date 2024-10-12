import re
import cv2
from typing import List
import numpy as np

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

def plot_annotations(image:np.ndarray, annotations: List)->np.ndarray:
    height, width, channel = image.shape
    # bytes_per_line = 3 * width

    # Clear previous drawings on the image
    image_copy = image.copy()

    # Define a list of colors for different boxes
    colors = [
        (230, 100, 0), (0, 177, 177), (0, 0, 222),
        (211, 222, 0), (200, 0, 200), (0, 255, 255)
    ]

    # Calculate font scale based on image size
    font_scale = max(0.5, min(width, height) / 800.0)

    # Draw boxes and labels on the image before displaying it
    for i, box in enumerate(annotations):
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
    return image_copy
