from typing import Annotated
import cv2
import os
from av import AudioFrame
from av import VideoFrame
from aiortc import RTCSessionDescription

from fastapi import Body, Request, APIRouter
from fastapi.responses import HTMLResponse, FileResponse
from numpy import ndarray


from src import WebRTCApplication
from src import PeerConnection
from src import AudioTransformTrack, VideoTransformTrack
from src import OfferRTC
from settings import ROOT, TEMPLATES


router = APIRouter(
    prefix='/test',
    tags=['test'],
)

WebRTCApplication.routers.append(router)

@router.get('/page', response_class=HTMLResponse)
async def test_index(request: Request):
    return TEMPLATES.TemplateResponse('test.html', {'request': request})

@router.get('/script', response_class=FileResponse)
async def test_script():
    return FileResponse(os.path.join(ROOT, 'static/test.js'), media_type='text/javascript')

@router.post('/offer')
async def test_offer(offer: OfferRTC, video_transform: Annotated[str, Body()] = None):
    RTCoffer = RTCSessionDescription(sdp=offer.sdp, type=offer.type)
    pc = PeerConnection()

    def ping_pong(message, channel):
        if isinstance(message, str) and message.startswith("ping"):
            channel.send("pong" + message[4:])

    def dch_open(channel):
        channel.send("+++ opened")

    async def vtf(frame: ndarray, video_transform: str) -> ndarray:
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
    
    pc.bind_video_track(VideoTransformTrack(vtf, video_transform=video_transform))
    pc.bind_audio_track(AudioTransformTrack())

    pc.add_events_on_datachannel(on_message=ping_pong,
                                 on_open=dch_open)

    await pc.setRemoteDescription(RTCoffer)

    answer = await pc.createAnswer()

    await pc.setLocalDescription(answer)

    return OfferRTC(sdp=pc.localDescription.sdp,
                    type=pc.localDescription.type)