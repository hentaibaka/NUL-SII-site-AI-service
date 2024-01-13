from abc import abstractmethod
import logging
import uuid
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
        self.logger = logging.getLogger(__name__)

        self.logger.setLevel(logging.DEBUG)

    def bind_track(self, track: MediaStreamTrack) -> None:
        self.track = self.relay.subscribe(track, buffered=True)
        self.logger.debug(f"{self.track.kind} track {self.track.id} was binded")

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
 
        self._prev_processed_img = None

        self._this_track_time = 0
        self._this_track_prev_global_time = None
        self._this_track_prev_time = 0
        self._recieved_track_time = 0
        self._recieved_track_prev_time = 0
        self._process_time = 0
        self._delay = 0
        self._frames = 0
        self._copied_frames = 0
        self._diff = 0
        self._recieved_diff = 0
        self._this_diff = 0

    async def transform_frame(self, frame: VideoFrame) -> VideoFrame:

        start = time.time()
        #если задержка больше, чем время обработки кадра
        #возвращаем предыдущий кадр, иначе вычисляем новый кадр
        #чтобы вычисляемый трек сильно не отставал от получемого
        #и передача данных велась с минимальной задержкой
        #self._delay > self._process_time
        if (self._diff > self._this_diff and 
            not self._prev_processed_img is None):
            img = np.copy(self._prev_processed_img)
            self._copied_frames += 1
            #тут что-то поумнее придумать бы
            self._delay = 0 
        else:
            img = frame.to_ndarray(format="bgr24")
            img = await self.transformFunc(img, **self.kwargs)
            self._prev_processed_img = np.copy(img)
            self._frames += 1

        end = time.time()
        #замеряем время вычисления кадра
        self._process_time = end - start
        #устанавливаем время на полученном треке
        self._recieved_track_time = frame.time
        #вычисляем время на изменённом трека
        if self._this_track_prev_global_time is None:
            self._this_track_time = end - start
        else:
            self._this_track_time += end - self._this_track_prev_global_time
        #вычисляем разницу во времени на полученном и изменяемом треке
        #теоретически, эта разница всегда будет > 0
        self._diff = self._this_track_time - self._recieved_track_time
        #вычисляем сколько времени прошло с предыдущего кадра
        self._recieved_diff = self._recieved_track_time - self._recieved_track_prev_time
        self._this_diff = self._this_track_time - self._this_track_prev_time
        #вычисляем разницу во времени на кадр
        if d:=self._process_time - self._recieved_diff > 0:
            self._delay += d 
        #вычисляем текущий FPS
        recieved_fps = round(1 / self._recieved_diff) if self._recieved_diff else '-'
        this_fps = round(1 / self._this_diff) if self._this_diff else '-'
        #устанавливаем время(глобальное) на предыдущем кадре
        self._this_track_prev_global_time = end
        #устанавливаем время(относительное) на предыдущем кадре
        self._recieved_track_prev_time = self._recieved_track_time
        self._this_track_prev_time = self._this_track_time

        copied_perc = round(self._copied_frames * 100 / (self._copied_frames + self._frames))

        a = f'recived time {round(self._recieved_track_time, 1)} time {round(self._this_track_time, 1)} diff {round(self._diff, 1)}'
        b = f'recived FPS {recieved_fps} this FPS {this_fps} delay {round(self._delay, 3)}'
        c = f'copied {copied_perc}%'

        cv2.putText(img, a, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(img, b, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(img, c, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        self.logger.debug(" ".join([a, b, c]))

        new_frame = VideoFrame.from_ndarray(img, format="bgr24")

        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base

        return new_frame    

    async def recv(self) -> VideoFrame:
        if self.track:
            frame = await self.track.recv()

            if self.transformFunc:
                new_frame = await self.transform_frame(frame)
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