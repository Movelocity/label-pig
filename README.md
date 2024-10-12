## Label Pig
AI 辅助标注视频目标标注工具，使用 grounding dino 服务进行视频目标检测

![](./doc/main_window.jpg)

## 如何使用
初次使用需要安装依赖
```bash
python -m pip install -r requirements.txt

# 运行主文件
python main.py
```

Python 版本 3.5 以上均可，有问题可以提 issue

## 数据
将所有需要标注的视频放置在 `videos` 文件夹下，然后运行 `main.py` 即可自动检测有哪些视频

## 服务端
需要 GroundingDino 图像标注服务，目前我自己搭建，服务不一定全天在线。后续将更新个人部署服务的代码

## Todo
- [x] 任意帧增加标注，删除标注，展示时间维度已有标注并允许跳转
- [ ] 区间标注功能
- [ ] 标注数据导出为 Ultralitics 支持的格式
- [ ] 样式优化