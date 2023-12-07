import logging
import os
from aiortc import RTCSessionDescription
import cv2
from av import VideoFrame

from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse, FileResponse

from src import WebRTCApplication
from src import PeerConnection
from src import VideoTransformTrack
from src import OfferRTC
from settings import ROOT, TEMPLATES

from .dedsad_project import DedSad


router = APIRouter(
    prefix='/dedsad',
    tags=['dedsad'],
)

WebRTCApplication.routers.append(router)

@router.get('/page', response_class=HTMLResponse)
async def test_index(request: Request):
    return TEMPLATES.TemplateResponse('dedsad.html', {'request': request})

@router.get('/script', response_class=FileResponse)
async def test_script():
    return FileResponse(os.path.join(ROOT, 'static/dedsad.js'), media_type='text/javascript')

@router.post('/offer')
async def test_offer(offer: OfferRTC):
    RTCoffer = RTCSessionDescription(sdp=offer.sdp, type=offer.type)
    pc = PeerConnection()
    pc.bind_video_track(VideoTransformTrack(DedSad.run))
    await pc.setRemoteDescription(RTCoffer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    return OfferRTC(sdp=pc.localDescription.sdp,
                    type=pc.localDescription.type)