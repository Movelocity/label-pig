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
需要 GroundingDino 图像标注服务，可以直接使用他人搭建好的。本人的服务地址已经在代码里，但是不保证服务24小时在线。

如果需要自己部署:
1. 在 `./service` 文件夹下有额外的依赖 `requirements.txt`，安装它里面的依赖

2. 同时准备 pytorch (建议在有Nvidai显卡的主机上安装cuda版的torch)

3. 需要一个模型文件`groundingdino_swint_ogc.pth`，放到 `./service/groundingdino/weights/groundingdino_swint_ogc.pth`

4. 在 `service` 文件夹下运行 `python run_api.py`

5. 修改 `modules/api.py` 里的 `BASE_URL` 为自己的服务地址，然后重启主程序

## Todo
- [x] 任意帧增加标注，删除标注，展示时间维度已有标注并允许跳转
- [ ] 区间标注功能
- [ ] 标注数据导出为 Ultralitics 支持的格式
- [ ] 样式优化