from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from groundingdino.util.inference import load_model, predict, transform_image, annotate
from PIL import Image
import numpy as np
import base64
import io
import cv2

# 创建 FastAPI 应用
app = FastAPI()

# 允许来自任何来源的 CORS 请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加载模型
cfg_path = "groundingdino/config/GroundingDINO_SwinT_OGC.py"
weight_path = "groundingdino/weights/groundingdino_swint_ogc.pth"

import os  # huggingface 模型检查和下载需要代理
tmp_proxy = "http://localhost:7890"
if tmp_proxy:
    os.environ['HTTP_PROXY'] = 'http://localhost:7890'
    os.environ['HTTPS_PROXY'] = 'http://localhost:7890'
model = load_model(cfg_path, weight_path).cuda()  # 下载模型
if tmp_proxy:
    os.environ['HTTP_PROXY'] = ''
    os.environ['HTTPS_PROXY'] = ''

# 定义 POST 路由
@app.post("/groundingdino/detect")
async def detect(
    image: UploadFile = File(...),        # 接收图像文件
    caption: str = Form(...),             # 接收文本提示 "animal . eye . nose . xxx ."
    box_threshold: str = Form("0.35"),    # 可选，框阈值
    text_threshold: str = Form("0.25"),   # 可选，文本阈值
    return_type: str = Form("annotation") # 可选，返回类型 'annotation' | 'preview' | 'file'
):
    # 读取图像
    image_data = await image.read()
    image_input = Image.open(io.BytesIO(image_data)).convert("RGB")

    # 预处理图像
    pt_image = transform_image(image_input)

    # 转换阈值为浮点数
    box_threshold = float(box_threshold)
    text_threshold = float(text_threshold)

    # 预测
    boxes, logits, phrases = predict(
        model=model,
        image=pt_image,
        caption=caption,
        box_threshold=box_threshold,
        text_threshold=text_threshold
    )

    if return_type == "preview":
        # 生成带注释的图像
        annotated_frame = annotate(
            image_source=np.asarray(image_input),
            boxes=boxes,
            logits=logits,
            phrases=phrases
        )

        # 将图像转换为 Base64 编码
        _, im_arr = cv2.imencode('.jpg', annotated_frame)
        im_bytes = im_arr.tobytes()
        im_b64 = base64.b64encode(im_bytes).decode('utf-8')

        # 返回 HTML 响应
        html_content = f"""
        <html>
        <body>
        <img src="data:image/jpeg;base64,{im_b64}" />
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    elif return_type == 'file':
        # 生成带注释的图像
        annotated_frame = annotate(
            image_source=np.asarray(image_input),
            boxes=boxes,
            logits=logits,
            phrases=phrases
        )

        # 将图像编码为字节流
        _, im_arr = cv2.imencode('.jpg', annotated_frame)
        im_bytes = im_arr.tobytes()
        image_stream = io.BytesIO(im_bytes)

        # 返回流式响应
        return StreamingResponse(
            content=image_stream,
            media_type='image/jpeg',
            headers={"Content-Disposition": "attachment; filename=annotated_image.jpg"}
        )

    # 默认返回注释结果
    return JSONResponse(content={
        "boxes": boxes.tolist(),
        "logits": logits.tolist(),
        "phrases": phrases
    })

@app.get('/info')
def get_info():
    return JSONResponse(content={'msg': "hello"})

# 运行应用时使用以下命令：
# uvicorn run_api:app --reload --port 8080
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("run_api:app", host="0.0.0.0", port=8081, reload=True)