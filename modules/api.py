import cv2
import requests
import numpy as np
import io

BASE_URL = "http://112.74.74.13:30770"
# BASE_URL = "http://localhost:8081"


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
    
    # 返回样本
    # resultObj = {  
    #     'msg': 'success'
    #     'boxes': [
    #         [0.2300889492034912, 0.43166184425354004, 0.42723730206489563, 0.5608834624290466],  // [cx, cy, w, h]
    #         [0.7489202618598938, 0.45753565430641174, 0.4995116591453552, 0.7285897731781006]
    #     ], 
    #     'logits': [0.5680023431777954, 0.5597519278526306], 
    #     'phrases': ['fruit', 'fruit']
    # }
    try:
        response = requests.post(url, files=files, timeout=20)
        if response.status_code == 200:  # 请求成功
            resultObj = response.json()
            resultObj['msg'] = "success"
            return resultObj
        return {"msg": f"{response.status_code}, {response.text}"}
    except requests.RequestException as e:
        return {"msg": str(e)}
