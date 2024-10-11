import os
import json 
from typing import List, Dict
from pathlib import Path

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data, pretty=False):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2 if pretty else None)

class Label:
    """
    cx, cy, w, h, name
    """
    def __init__(self, cx, cy, w, h, name):
        self.cx = cx
        self.cy = cy
        self.w = w
        self.h = h
        self.name = name
    
    def toDict(self):
        return {
            "cx": self.cx,
            "cy": self.cy,
            "w": self.w,
            "h": self.h,
            "name": self.name
        }

    def __str__(self):
        return f"{self.cx}, {self.cy}, {self.w}, {self.h}, {self.name}"

class LabelManager:
    def __init__(self, video_path: Path):
        self.video_path = video_path
        self.time_points = []
        self.labels: Dict[Label] = {}  # 时间点: 标签组
        self.load()

    def add_labels(self, timestamp: str, labels: List[Label]):
        """增加一个时间点上的多个物体标签"""
        self.labels[timestamp] = labels
        if timestamp not in self.time_points:
            self.time_points.append(timestamp)
            self.time_points.sort()
        self.save()

    def save(self):
        filepath = f'./labels/{self.video_path.stem}.json'
        data = {timestamp: [label.toDict() for label in labels] for timestamp, labels in self.labels.items()}
        save_json(filepath, data, pretty=False)

    def load(self):
        filepath = f'./labels/{self.video_path.stem}.json'
        if os.path.exists(filepath):
            labels_with_time = load_json(filepath)
            for timestamp, labels in labels_with_time.items():
                self.labels[timestamp] = [Label(**labelDict) for labelDict in labels]
            self.time_points = sorted(list(self.labels.keys()))

            print('load labels: ', len(self.time_points))

