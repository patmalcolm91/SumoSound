"""
Contains classes for vehicle sounds
"""

from openal import *


class VehicleSound:
    def __init__(self, file, base_gain=1, relative_position=None, looping=True):
        self.file = file
        self.base_gain = base_gain
        self.relative_position = relative_position if relative_position is not None else (0, 0, 0)
        self.source = oalOpen(self.file)
        self.source.set_looping(looping)

    def play(self):
        self.source.play()

    def pause(self):
        self.source.pause()

    def set_gain(self, gain):
        resultant_gain = self.base_gain * gain
        self.source.set_gain(resultant_gain)

    def set_position(self, position):
        self.source.set_position(position)

    def set_velocity(self, velocity):
        self.source.set_velocity(velocity)
