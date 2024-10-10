import cv2
import httpx
import requests
import numpy as np
import io
from . label_dialog import Label

BASE_URL = "http://112.74.74.13:30770"
# BASE_URL = "http://localhost:8081"


# async def image_detect_api_async(image: np.ndarray, caption: str = 'fruit'):
#     """ image颜色通道为 bgr """
#     url = BASE_URL + "/groundingdino/detect"
#     # Encode the image to a memory buffer
#     _, buffer = cv2.imencode('.jpg', image)  # You can change .png to .jpg if needed
    
#     # Create a BytesIO object
#     image_bytes = io.BytesIO(buffer)

#     # Prepare files for the request
#     files = {
#         'image': ('image.jpg', image_bytes, 'image/jpeg'),  # Specify content type
#         'caption': (None, caption),
#         'return_type': (None, 'annotation')
#     }
#     print("send to: "+url)
#     # try:
#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, files=files, timeout=20)
#         print(response)
#         if response.status_code == 200:  # 请求成功
#             result = response.json()
#             result['msg'] = "success"
#             return result
#         return {"msg": f"{response.status_code}, {response.text}"}  # 状态码不是200，则认为是错误
    # except Exception as e:
    #     # 捕获异常并返回具体的错误信息
    #     error_message = f"请求出错: {str(e)}"
    #     return {"msg": error_message}


def image_detect_api(image: np.ndarray, caption: str = 'fruit'):
    """ image颜色通道为 bgr """
    url = BASE_URL + "/groundingdino/detect"
    # Encode the image to a memory buffer
    _, buffer = cv2.imencode('.jpg', image)  # You can change .png to .jpg if needed
    
    # Create a BytesIO object
    image_bytes = io.BytesIO(buffer)

    # Prepare files for the request
    files = {
        'image': ('image.jpg', image_bytes, 'image/jpeg'),  # Specify content type
        'caption': (None, caption),
        'return_type': (None, 'annotation')
    }
    # print("send to: " + url)
    
    # Send the request using requests library
    try:
        response = requests.post(url, files=files, timeout=10)
        if response.status_code == 200:  # 请求成功
            resultObj = response.json()
            resultObj['msg'] = "success"
            return resultObj
        return {"msg": f"{response.status_code}, {response.text}"}
    except requests.RequestException as e:
        return {"msg": str(e)}

"""
{
    "boxes":[
        [0.6651382446289062,0.690296471118927,0.3931420147418976,0.5836743116378784],
        [0.7651753425598145,0.44946327805519104,0.36681067943573,0.5355294942855835],
        [0.19807128608226776,0.4881398379802704,0.3607184588909149,0.39982813596725464],
        [0.4723019599914551,0.13063563406467438,0.2897445559501648,0.26055923104286194]
    ],
    "logits":[
        0.6775819659233093,0.6441808342933655,0.432659387588501,0.3567177653312683
    ],
    "phrases":[
        "cup","cup","cup","cup"
    ]}
"""