"""
Contains classes for vehicle sounds
"""

from openal import *
from typing import Union, Tuple, List

_buffers = dict()  # a dict with file paths as keys and the corresponding buffers as values


class VehicleSound:
    """
    Wrapper class for an OpenAL source with properties to store relative position on vehicle and other parameters.
    """
    def __init__(self, file, base_gain=1, relative_position=None, looping=True, enabled=False):
        """
        Initializes a VehicleSound object.
        :param file: path to the sound file (mono .wav for best results)
        :param base_gain: baseline level of gain for the sound. Acts as baseline when gain is modulated.
        :param relative_position: position of the sound relative to the vehicle point.
        :param looping: whether or not the sound should be set to loop
        :param enabled: whether or not the sound should be enabled by default
        :type file: str
        :type base_gain: float
        :type relative_position: Tuple[float, float, float]
        :type looping: bool
        :type enabled: bool
        """
        self.file = file
        self.base_gain = base_gain
        self.relative_position = relative_position if relative_position is not None else (0, 0, 0)
        if self.file not in _buffers:
            _buffers[self.file] = Buffer(WaveFile(self.file))
        self.source = None
        self.enabled = enabled
        self.playing = False
        self.looping = looping
        self.position = (0, 0, 0)
        self.velocity = (0, 0, 0)
        if enabled:
            self.enable()

    def enable(self):
        self.source = Source(_buffers[self.file])
        self.source.set_looping(self.looping)
        self.enabled = True
        self.set_position(self.position)
        self.set_velocity(self.velocity)
        if self.playing:
            self.play()

    def disable(self):
        if self.source is not None:
            self.source.destroy()
        self.source = None
        self.enabled = False

    def play(self):
        """Plays the vehicle sound."""
        self.playing = True
        if self.enabled:
            self.source.play()

    def pause(self):
        """Pauses the vehicle sound."""
        self.playing = False
        if self.enabled:
            self.source.pause()

    def set_gain(self, gain):
        """Sets the gain of the sound (applied on top of the base gain)."""
        if self.enabled:
            resultant_gain = self.base_gain * gain
            self.source.set_gain(resultant_gain)

    def set_position(self, position):
        """
        Sets the position of the sound (absolute coordinates).
        :param position: position for the sound.
        :return: None
        :type position: Tuple[float, float, float]
        """
        self.position = position
        if self.enabled:
            self.source.set_position(position)

    def set_velocity(self, velocity):
        """
        Sets the velocity vector of the sound (absolute coordinates).
        :param velocity: velocity vector for the sound
        :return: None
        :type velocity: Union[Tuple, List][float, float, float]
        """
        self.velocity = velocity
        if self.enabled:
            self.source.set_velocity(velocity)

    def __del__(self):
        if self.enabled:
            try:
                self.source.destroy()
                del self.source
            except al.ALError:
                pass
