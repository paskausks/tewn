import pyaudio
import struct

from math import ceil
from typing import (Generator, Any)


class MicrophoneInputException(Exception):
    pass


class MicrophoneInput(object):
    """
    Capture audio input
    """
    def __init__(self):
        # Initialize PyAudio
        self._sys = pyaudio.PyAudio()
        self._sample_fmt = pyaudio.paInt32
        self._frames_per_buf = 1024

        self._buf = b''

        # Get default device
        try:
            self._dev = self._sys.get_default_input_device_info()
        except IOError:
            raise MicrophoneInputException(
                'Couldn\'t get default input device info.'
            )

        # Set up an input stream for the default device
        self._stream = self._sys.open(
            self.sample_rate,
            1,  # Mono
            self._sample_fmt,  # Sampling format
            input=True,
            input_device_index=self._dev['index'],
            start=False,
            frames_per_buffer=self._frames_per_buf,
            stream_callback=self._stream_cb
        )

    def listen(self):
        """
        Start receiving data from input
        """
        self._stream.start_stream()

    def _stream_cb(
        self, in_data: bytes, frame_count: int,
        time_info: dict, status_flags: int
    ) -> tuple:
        """
        Callback for the stream listener.
        :param in_data: recorded data
        :param frame_count: number of frames read
        :param time_info:  dictionary with the following keys:
            input_buffer_adc_time, current_time, and output_buffer_dac_time
        :param status_flags: one of PortAudio Callback flags
        :return: tuple of (out_data, flag)
        """
        # Just store the data frames received and continue,
        # so the callback finishes as fast as possible.
        self._buf += in_data
        return None, pyaudio.paContinue

    @property
    def device_name(self) -> str:
        """
        :return: Name of default device
        """
        return self._dev['name']

    @property
    def sample_rate(self) -> int:
        return int(self._dev['defaultSampleRate'])

    @property
    def sample_size(self) -> int:
        return pyaudio.get_sample_size(self._sample_fmt)

    @property
    def _frames(self) -> Generator[int, Any, None]:
        """
        Split and unpack the received data into sample frames
        :return: iterator of audio sample frames as integers
        """
        sample_size = self.sample_size
        sample_count = ceil(len(self._buf) / sample_size)
        return (self._unpack_frame(
            self._buf[i * sample_size:(i + 1) * sample_size]
        ) for i in range(sample_count))

    @property
    def frames(self) -> list:
        """
        Return audio frames and clear buffer
        :return: recorded frames as unpacked integers
        """
        rv = list(self._frames)
        self._buf = b''
        return rv

    @staticmethod
    def _unpack_frame(frame: bytes) -> int:
        """
        Convert an audio frame to an 32 bit integer
        :param frame:
        :return: Audio frame
        """
        return struct.unpack('i', frame)[0]

    def quit(self):
        self._stream.stop_stream()
        self._stream.close()
        self._sys.terminate()

    def __repr__(self) -> str:
        return '<%s: %s at %dkHz>' % (
            self.__class__.__name__,
            self.device_name,
            self.sample_rate
        )
