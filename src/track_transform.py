from abc import abstractmethod
import asyncio
import fractions
import time
from typing import Any, Callable, Coroutine
import cv2
import numpy as np

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
                 transformFunc: Callable[[np.ndarray, dict[str, Any]], Coroutine[Any, Any, np.ndarray]] = None, 
                 **kwargs: dict[str, Any]) -> None:
        super().__init__()

        self.relay = MediaRelay()
        self.track: MediaStreamTrack = None
        self.transformFunc = transformFunc
        self.kwargs = kwargs

    def bind_track(self, track: MediaStreamTrack) -> None:
        self.track = self.relay.subscribe(track, buffered=True)

    @abstractmethod
    async def recv(self) -> VideoFrame | AudioFrame:
        pass

    @abstractmethod
    async def transform_frame(self, frame: VideoFrame | AudioFrame) -> VideoFrame | AudioFrame:
        pass

class VideoTransformTrack(MediaTransformTrack):
    kind = "video"

    def __init__(self, 
                 videoTransformFunc: Callable[[np.ndarray, dict[str, Any]], Coroutine[Any, Any, np.ndarray]] = None, 
                 **kwargs: dict[str, Any]):
        super().__init__(videoTransformFunc, **kwargs)

        self._start_time = None
        self._prev_diff = 0
        self._prev_track_time = 0 
        self._prev_real_time = 0
        self._prev_process_time = 0
        self._prev_processed_img = None
        self._delay = 0

    def transform_frame(self, frame: VideoFrame) -> VideoFrame:
        start = time.time()

        if (not self._prev_processed_img is None and
            self._delay >= self._prev_process_time):
            img = np.copy(self._prev_processed_img)
        else:
            img = frame.to_ndarray(format="bgr24")
            img = self.transformFunc(img, **self.kwargs)
            self._prev_processed_img = np.copy(img)

        end = time.time()

        self._prev_process_time = end - start

        if self._start_time is None:
            self._start_time = time.time()
            #когда минусовая разница
            #надо исправлять 
            #видео передаваться стало позже чем надо
            #считать не делей а сколько времени прошло с отрисовки прошлого кадра 

        track_time = frame.time
        real_time = time.time() - self._start_time
        self._delay = real_time - track_time

        track_frame_time = track_time - self._prev_track_time
        real_frame_time = real_time - self._prev_real_time

        self._prev_track_time = track_time
        self._prev_real_time = real_time

        track_fps = round(1 / track_frame_time) if track_frame_time else '-'
        real_fps = round(1 / real_frame_time) if real_frame_time else '-' 

        diff = real_time - track_time
        delta_diff = diff - self._prev_diff
        self._prev_diff = diff

        a = f'tt {round(track_time, 1)} rt {round(real_time, 1)} diff {round(diff, 3)} delta diff {round(delta_diff, 3)}'
        b = f'TFPS {track_fps} RFPS {real_fps}'

        cv2.putText(img, a, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(img, b, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        new_frame = VideoFrame.from_ndarray(img, format="bgr24")

        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base

        return new_frame    

    async def recv(self) -> VideoFrame:
        if self.track:
            frame = await self.track.recv()

            if self.transformFunc:
                new_frame = self.transform_frame(frame)
                return new_frame
            else:
                return frame
        else:
            return await VideoStreamTrack.recv()

class AudioTransformTrack(MediaTransformTrack):
    kind = "audio"

    def __init__(self,  
                 audioTransformFunc: Callable[[np.ndarray, dict[str, Any]], Coroutine[Any, Any, np.ndarray]] = None, 
                 **kwargs: dict[str, Any]):
        super().__init__(audioTransformFunc, **kwargs)

    async def transform_frame(self, frame: AudioFrame) -> AudioFrame:
        audio = frame.to_ndarray(format="s16")

        audio = await self.transformFunc(audio, **self.kwargs)

        new_frame = AudioFrame.from_ndarray(audio, format="s16")

        new_frame.pts = frame.pts
        new_frame.sample_rate = frame.sample_rate
        new_frame.time_base = frame.time_base

        return new_frame

    async def recv(self) -> AudioFrame:
        if self.track:
            frame = await self.track.recv()
            
            if self.transformFunc:
                new_frame = await self.transform_frame(frame)
                return new_frame
            else:
                return frame
        else:
            return await MyAudioStreamTrack.recv()
            #return await AudioStreamTrack.recv()