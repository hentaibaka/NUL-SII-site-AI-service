from abc import abstractmethod
import asyncio
import fractions
import time
from typing import Any, Callable, Coroutine

from aiortc import MediaStreamTrack, VideoStreamTrack#, AudioStreamTrack - смотреть этот класс ниже
from aiortc.contrib.media import MediaRelay

from av import AudioFrame
from av import VideoFrame
from av.frame import Frame
from av.packet import Packet


########################################################################################
# Разрабы пидорасы, забыли добавить AudioStreamTrack в __init__ файл библиотеки aiortc #
## Если заработает импорт, написанный ниже, удалить нахуй всё что между комментариев  ##
########################################################################################

#⠄⠄⠄⢰⣧⣼⣯⠄⣸⣠⣶⣶⣦⣾⠄⠄⠄⠄⡀⠄⢀⣿⣿⠄                      ⠄⣿⣿⢀⠄⡀⠄⠄⠄⠄⣾⣦⣶⣶⣠⣸⠄⣯⣼⣧⢰⠄⠄⠄
#⠄⠄⠄⣾⣿⠿⠿⠶⠿⢿⣿⣿⣿⣿⣦⣤⣄⢀⡅⢠⣾⣛⡉⠄                      ⠄⡉⣛⣾⢠⡅⢀⣄⣤⣦⣿⣿⣿⣿⢿⠿⠶⠿⠿⣿⣾⠄⠄⠄
#⠄⠄⢀⡋⣡⣴⣶⣶⡀⠄⠄⠙⢿⣿⣿⣿⣿⣿⣴⣿⣿⣿⢃⣤                      ⣤⢃⣿⣿⣿⣴⣿⣿⣿⣿⣿⢿⠙⠄⠄⡀⣶⣶⣴⣡⡋⢀⠄⠄
#⠄⠄⢸⣇⠻⣿⣿⣿⣧⣀⢀⣠⡌⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿      ###    ###      ⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢻⡌⣠⢀⣀⣧⣿⣿⣿⠻⣇⢸⠄⠄
#⠄⢀⢸⣿⣷⣤⣤⣤⣬⣙⣛⢿⣿⣿⣿⣿⣿⣿⡿⣿⣿⡍⠄⠄     #   #  #   #     ⠄⠄⡍⣿⣿⡿⣿⣿⣿⣿⣿⣿⢿⣛⣙⣬⣤⣤⣤⣷⣿⢸⢀⠄
#⠄⣼⣖⣿⣿⣿⣿⣿⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⢇⣿⣿⡷⠶⠶    #     ##     #    ⠶⠶⡷⣿⣿⢇⣿⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣖⣼⠄
#⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣽⣿⣿⣿⡇⣿⣿⣿⣿⣿⣿     #  aiortc  #     ⣿⣿⣿⣿⣿⣿⡇⣿⣿⣿⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠘
#⢀⠈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿      ##      ##      ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢿⠈⢀
#⢸⣿⣦⣌⣛⣻⣿⣿⣧⠙⠛⠛⡭⠅⠒⠦⠭⣭⡻⣿⣿⣿⣿⣿        ##  ##        ⣿⣿⣿⣿⣿⡻⣭⠭⠦⠒⠅⡭⠛⠛⠙⣧⣿⣿⣻⣛⣌⣦⣿⢸
#⠘⣿⣿⣿⣿⣿⣿⣿⣿⡆⠄⠄⠄⠄⠄⠄⠄⠄⠹⠈⢋⣽⣿⣿          ##          ⣿⣿⣽⢋⠈⠹⠄⠄⠄⠄⠄⠄⠄⠄⡆⣿⣿⣿⣿⣿⣿⣿⣿⠘
#⠄⠘⣿⣿⣿⣿⣿⣿⣿⣿⠄⣴⣿⣶⣄⠄⣴⣶⠄⢀⣾⣿⣿⣿                      ⣿⣿⣿⣾⢀⠄⣶⣴⠄⣄⣶⣿⣴⠄⣿⣿⣿⣿⣿⣿⣿⣿⠘⠄
#⠄⠄⠈⠻⣿⣿⣿⣿⣿⣿⡄⢻⣿⣿⣿⠄⣿⣿⡀⣾⣿⣿⣿⣿                      ⣿⣿⣿⣿⣾⡀⣿⣿⠄⣿⣿⣿⢻⡄⣿⣿⣿⣿⣿⣿⠻⠈⠄⠄
#⠄⠄⠄⠄⠈⠛⢿⣿⣿⣿⠁⠞⢿⣿⣿⡄⢿⣿⡇⣸⣿⣿⠿⠛                      ⠛⠿⣿⣿⣸⡇⣿⢿⡄⣿⣿⢿⠞⠁⣿⣿⣿⢿⠛⠈⠄⠄⠄⠄
#⠄⠄⠄⠄⠄⠄⠄⠉⠻⣿⣿⣾⣦⡙⠻⣷⣾⣿⠃⠿⠋⠁⠄⠄                      ⠄⠄⠁⠋⠿⠃⣿⣾⣷⠻⡙⣦⣾⣿⣿⠻⠉⠄⠄⠄⠄⠄⠄⠄


#from aiortc import AudioStreamTrack

AUDIO_PTIME = 0.020  # 20ms audio packetization

class MediaStreamError(Exception):
    pass

class MyAudioStreamTrack(MediaStreamTrack):
    """
    A dummy audio track which reads silence.
    """

    kind = "audio"

    _start: float
    _timestamp: int

    async def recv(self) -> Frame:
        """
        Receive the next :class:`~av.audio.frame.AudioFrame`.

        The base implementation just reads silence, subclass
        :class:`AudioStreamTrack` to provide a useful implementation.
        """
        if self.readyState != "live":
            raise MediaStreamError

        sample_rate = 8000
        samples = int(AUDIO_PTIME * sample_rate)

        if hasattr(self, "_timestamp"):
            self._timestamp += samples
            wait = self._start + (self._timestamp / sample_rate) - time.time()
            await asyncio.sleep(wait)
        else:
            self._start = time.time()
            self._timestamp = 0

        frame = AudioFrame(format="s16", layout="mono", samples=samples)
        for p in frame.planes:
            p.update(bytes(p.buffer_size))
        frame.pts = self._timestamp
        frame.sample_rate = sample_rate
        frame.time_base = fractions.Fraction(1, sample_rate)
        return frame

#######################################################################################
################################### Удалять до сюда ###################################
#######################################################################################

class MediaTransformTrack(MediaStreamTrack):
    def __init__(self,
                 transformFunc: Callable[[VideoFrame | AudioFrame, dict[str, Any]], Coroutine[Any, Any, VideoFrame | AudioFrame]] = None, 
                 **kwargs: dict[str, Any]) -> None:
        super().__init__()

        self.relay = MediaRelay()
        self.track: MediaStreamTrack = None
        self.transformFunc = transformFunc
        self.kwargs = kwargs

    def bind_track(self, track: MediaStreamTrack) -> None:
        self.track = self.relay.subscribe(track, buffered=False)

    @abstractmethod
    async def recv(self) -> VideoFrame | AudioFrame:
        pass

class VideoTransformTrack(MediaTransformTrack):
    kind = "video"

    def __init__(self, 
                 videoTransformFunc: Callable[[VideoFrame, dict[str, Any]], VideoFrame] = None, 
                 **kwargs: dict[str, Any]):
        super().__init__(videoTransformFunc, **kwargs)

    async def recv(self) -> VideoFrame:
        if self.track:
            frame = await self.track.recv()

            if self.transformFunc:
                return await self.transformFunc(frame, **self.kwargs) 
            else:
                return frame
        else:
            return await VideoStreamTrack.recv()

class AudioTransformTrack(MediaTransformTrack):
    kind = "audio"

    def __init__(self,  
                 audioTransformFunc: Callable[[AudioFrame, dict[str, Any]], Coroutine[Any, Any, AudioFrame]] = None, 
                 **kwargs: dict[str, Any]):
        super().__init__(audioTransformFunc, **kwargs)

    async def recv(self) -> AudioFrame:
        if self.track:
            frame = await self.track.recv()
            
            if self.transformFunc:
                return await self.transformFunc(frame, **self.kwargs) 
            else:
                return frame
        else:
            return await MyAudioStreamTrack.recv()
            #return await AudioStreamTrack.recv()