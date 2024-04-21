import os
from typing import Annotated
import cv2
import numpy as np
from PIL import Image
from io import BytesIO

from fastapi import Body, File, Form, Request, APIRouter, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse

from src import Application
from settings import ROOT, TEMPLATES


router = APIRouter(
    prefix='/test',
    tags=['test'],
)

Application.routers.append(router)

@router.get('/page', response_class=HTMLResponse)
async def test_index(request: Request):
    return TEMPLATES.TemplateResponse('test_photo.html', {'request': request})

def transform_image(frame, video_transform):
    if video_transform == "cartoon":
        img_color = cv2.pyrDown(cv2.pyrDown(frame))
        for _ in range(6):
            img_color = cv2.bilateralFilter(img_color, 9, 9, 7)
        img_color = cv2.pyrUp(cv2.pyrUp(img_color))

        img_edges = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        img_edges = cv2.adaptiveThreshold(
            cv2.medianBlur(img_edges, 7),
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            9,
            2,
        )
        img_edges = cv2.cvtColor(img_edges, cv2.COLOR_GRAY2RGB)

        new_frame = cv2.bitwise_and(img_color, img_edges)
        return new_frame
    elif video_transform == "edges":
        new_frame = cv2.cvtColor(cv2.Canny(frame, 100, 200), cv2.COLOR_GRAY2BGR)
        return new_frame
    elif video_transform == "rotate":
        rows, cols, _ = frame.shape
        M = cv2.getRotationMatrix2D((cols / 2, rows / 2), 45, 1)
        new_frame = cv2.warpAffine(frame, M, (cols, rows))
        return new_frame
    else:
        return frame

@router.post('/offer')
async def test_offer(file: Annotated[UploadFile, File()] = None, 
                     video_transform: Annotated[str, Form()] = None):
    if file is None: return {'hello': 'world'}
    #преобразовываем файл в np.array
    image = np.array(Image.open(file.file))
    
    #выполняем обработку изображения

    image = transform_image(image, video_transform)

    #преобразовываем np.array в PIL.Image
    processed_image = Image.fromarray(image)
    #преобразовываем PIL.Image в бинарный формат
    image_bytes = BytesIO()
    processed_image.save(image_bytes, 'JPEG')
    image_bytes.seek(0)
    
    return StreamingResponse(image_bytes, media_type='image/jpeg')

@router.get('/script', response_class=FileResponse)
async def test_script():
    return None
