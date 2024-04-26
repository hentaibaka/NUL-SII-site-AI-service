import logging
from uuid import uuid4
from typing import Any, Callable, Coroutine

from aiortc import (RTCPeerConnection, RTCDataChannel, 
                    RTCSessionDescription, MediaStreamTrack)

from .track_transform import AudioTransformTrack, VideoTransformTrack
from .peer_connections_manager import PeerConnectionsManager

class PeerConnection():
    logger = logging.getLogger('pc')

    def __init__(self):
        self.pc = RTCPeerConnection()
        self.id = f'PeerConnection({uuid4()})'

        self.log_info('Created')

        PeerConnectionsManager.add(self)

        self._add_logger_on_datachannel()
        self._add_logger_on_track()
        self._add_logger_on_connectionstatechange()

    @property
    def RTCPeerConnection(self) -> RTCPeerConnection:
        return self.pc

    @property
    def connectionState(self) -> str:
        return self.pc.connectionState
    
    @property
    def localDescription(self) -> RTCSessionDescription:
        return self.pc.localDescription
    
    @property
    def remoteDescription(self) -> RTCSessionDescription:
        return self.pc.remoteDescription
    
    async def close(self):
       await self.pc.close() 
    
    def log_info(self, msg: str) -> None:
        self.logger.info(self.id + ' ' + msg)
    
    def add_events_on_datachannel(self, 
                                  on_open: Callable[[RTCDataChannel], None] = None,
                                  on_close: Callable[[RTCDataChannel], None] = None,
                                  on_message: Callable[[bytes | str, RTCDataChannel], None] = None,
                                  ) -> None:
        @self.pc.on('datachannel')
        def on_datachannel(channel: RTCDataChannel):
            if on_open:
                on_open(channel)
        
            if on_close:
                @channel.on("close")
                def close():
                    on_close(channel)
            
            if on_message:
                @channel.on("message")
                def message(message):
                    on_message(message, channel)
    
    def _add_logger_on_datachannel(self) -> None:
        @self.pc.on('datachannel')
        def on_datachannel(channel: RTCDataChannel):
            self.log_info(f'DataChannel {channel.id} opened')
        
            @channel.on("close")
            def close():
                self.log_info(f'DataChannel {channel.id} closed')
            
            @channel.on("message")
            def message(message):
                self.log_info(f'DataChannel {channel.id} recieved message')

    def _add_logger_on_connectionstatechange(self) -> None:
        @self.pc.on("connectionstatechange")
        async def on_connectionstatechange():
            if self.pc.connectionState == "failed":
                await self.pc.close()
            elif self.pc.connectionState == "closed":
                PeerConnectionsManager.discard(self)
            
            self.log_info(f'Connection state is {self.pc.connectionState}')

    def bind_audio_track(self, audioTrackTransformer: AudioTransformTrack = None) -> None:
        @self.pc.on("track")
        def on_track(track: MediaStreamTrack) -> None:
            if track.kind == "audio" and audioTrackTransformer:
                audioTrackTransformer.bind_track(track)
                self.pc.addTrack(audioTrackTransformer)

    def bind_video_track(self, videoTrackTransformer: VideoTransformTrack = None) -> None:
        @self.pc.on("track")
        def on_track(track: MediaStreamTrack) -> None:
            if track.kind == "video" and videoTrackTransformer:
                videoTrackTransformer.bind_track(track)
                self.pc.addTrack(videoTrackTransformer)
    
    def add_events_on_track(self, 
                            on_started: Callable[[MediaStreamTrack], None] = None,
                            on_ended: Callable[[MediaStreamTrack], None] = None) -> None:
        @self.pc.on("track")
        def on_track(track: MediaStreamTrack) -> None:
            on_started(track)
            @track.on("ended")
            async def ended():
                on_ended(track)      

    def _add_logger_on_track(self):
        @self.pc.on("track")
        def on_track(track: MediaStreamTrack) -> None:
            self.log_info(f'Track {track.kind} started')
            @track.on("ended")
            async def ended():
                self.log_info(f'Track {track.kind} ended')

    async def setRemoteDescription(self, sessionDescription: RTCSessionDescription) -> None:
        await self.pc.setRemoteDescription(sessionDescription)

    async def createAnswer(self) -> RTCSessionDescription | None:
        answer = await self.pc.createAnswer()
        return answer
    
    async def setLocalDescription(self, sessionDescription: RTCSessionDescription) -> None:
        await self.pc.setLocalDescription(sessionDescription)
        