"""
Contains classes for vehicle sounds
"""

from openal import *


class VehicleSound:
    """
    Wrapper class for an OpenAL source with properties to store relative position on vehicle and other parameters.
    """
    def __init__(self, file, base_gain=1, relative_position=None, looping=True):
        """
        Initializes a VehicleSound object.
        :param file: path to the sound file (mono .wav for best results)
        :param base_gain: baseline level of gain for the sound. Acts as baseline when gain is modulated.
        :param relative_position: position of the sound relative to the vehicle point.
        :param looping: whether or not the sound should be set to loop
        :type file: str
        :type base_gain: float
        :type relative_position: tuple[float, float, float]
        :type looping: bool
        """
        self.file = file
        self.base_gain = base_gain
        self.relative_position = relative_position if relative_position is not None else (0, 0, 0)
        self.source = oalOpen(self.file)
        self.source.set_looping(looping)

    def play(self):
        """Plays the vehicle sound."""
        self.source.play()

    def pause(self):
        """Pauses the vehicle sound."""
        self.source.pause()

    def set_gain(self, gain):
        """Sets the gain of the sound (applied on top of the base gain)."""
        resultant_gain = self.base_gain * gain
        self.source.set_gain(resultant_gain)

    def set_position(self, position):
        """
        Sets the position of the sound (absolute coordinates).
        :param position: position for the sound.
        :return: None
        :type position: tuple[float, float, float]
        """
        self.source.set_position(position)

    def set_velocity(self, velocity):
        """
        Sets the velocity vector of the sound (absolute coordinates).
        :param velocity: velocity vector for the sound
        :return: None
        :type velocity: tuple[float, float, float]
        """
        self.source.set_velocity(velocity)
