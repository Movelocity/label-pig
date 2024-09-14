
import cv2
import httpx
import numpy as np
import io

"""直接传bgr颜色的图"""
async def image_detect_api(image: np.ndarray, caption: str = 'fruit'):
    url = "http://112.74.74.13:30770/groundingdino/detect"
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
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, files=files)
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()  # or response.text if you expect plain text
        else:
            return {"error": response.status_code, "message": response.text}
        
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