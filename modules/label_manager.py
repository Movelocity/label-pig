import json 
from typing import List

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f)

class Label:
    def __init__(self, cx, cy, w, h, name):
        self.cx = cx
        self.cy = cy
        self.w = w
        self.h = h
        self.name = name


class LabelManager:
    def __init__(self):
        self.video_name = None
        self.time_points = []
        self.labels: List[Label] = {}  # 时间点: 标签组

    def add_labels(self, timestamp, labels):
        """增加一个时间点上的多个物体标签"""
        if timestamp in self.time_points:
            self.labels[timestamp] = labels
        else:
            self.time_points.append(timestamp)

    def save(self):
        filename = self.video_name.split('.')[0]
        filepath = f'./labels/{filename}.json'
        save_json(filepath, self.labels)

    def load(self):
        filename = self.video_name.split('.')[0]
        filepath = f'./labels/{filename}.json'
        self.labels = load_json(filepath)
        self.time_points = list(self.labels.keys())
