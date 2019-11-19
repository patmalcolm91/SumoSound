"""
Contains Vehicle classes and related classes and functions.
"""

import os
from .Sounds import *
import math
import traci
import traci.constants as tc
from typing import Any, Union, Callable, List, Tuple

_pkg_dir = os.path.dirname(os.path.abspath(__file__))


class Vehicle:
    def __init__(self, id):
        self.id = id
        traci.vehicle.subscribe(id, [tc.VAR_POSITION3D, tc.VAR_ANGLE, tc.VAR_SPEED])
        self.position = (0, 0, 0)
        self.angle = 0
        self.speed = 0
        self.acceleration = 0
        self.enabled = False
        self.sounds = []  # type: List[VehicleSound]
        self.signals = []  # type: List[Union[str, None]]
        self.response_curves = []  # type: List[Union[List[Tuple[float, float]], Callable[[Any], Union[float, int]]]]
        self.update_sounds()

    def add_sound(self, vehicle_sound, signal=None, response_curve=None):
        """
        Adds a VehicleSound with corresponding signal and response curve to the Vehicle.
        :param vehicle_sound: VehicleSound to add to Vehicle
        :param signal: attribute of Vehicle used to attenuate gain of vehicle_sound. Must be passed with response_curve
        :param response_curve: curve used to calculate gain from signal. May be callable or list of 2-length tuples.
        :return: None
        :type vehicle_sound: VehicleSound
        :type signal: str
        :type response_curve: Union[List[tuple[float, float]], Callable[[Any], Union[float, int]]]
        """
        if signal is not None and response_curve is None:
            raise TypeError("If signal is given, response_curve must also be given.")
        self.sounds.append(vehicle_sound)
        self.signals.append(signal)
        self.response_curves.append(response_curve)

    def _calculate_response_from_curve(self, curve, x):
        """
        Calculates the y value of the specified curve at x
        :param curve: response curve to use to calculate value
        :param x: input signal value
        :return: output of response curve at point corresponding to x
        :type curve: list[tuple[Union[float, int], Union[float, int]]]
        :type x: float
        """
        # clip output values at curve extents
        if x <= curve[0][0]:
            return curve[0][1]
        if x >= curve[-1][0]:
            return curve[-1][1]
        # if x is in the domain of the curve, interpolate the value
        for i in range(len(curve)-1):
            if x >= curve[i][0]:
                x0, y0 = curve[i]
                x1, y1 = curve[i+1]
                return y0 + (x - x0) * (y1 - y0) / (x1 - x0)

    def get_velocity_vector(self):
        geometric_angle = ((360 - self.angle + 90) % 360) * math.pi / 180
        vx = self.speed * math.cos(geometric_angle)
        vy = self.speed * math.sin(geometric_angle)
        return [vx, vy, 0]

    def update_sounds(self):
        for i, sound in enumerate(self.sounds):
            if self.signals[i] is None:
                continue
            try:
                signal_value = self.__getattribute__(self.signals[i])
            except AttributeError as err:
                raise ValueError("Signal " + self.signals[i] + " not in class " + self.__class__.__name__) from err
            else:
                if callable(self.response_curves[i]):
                    gain = self.response_curves[i](signal_value)
                else:
                    gain = self._calculate_response_from_curve(self.response_curves[i], signal_value)
                sound.set_gain(gain)
                pos = tuple([sound.relative_position[i] + self.position[i] for i in range(3)])
                sound.set_position(pos)
                sound.set_velocity(self.get_velocity_vector())

    def enable(self):
        self.enabled = True
        self.update_sounds()
        for sound in self.sounds:
            sound.enable()
            sound.play()

    def disable(self):
        self.enabled = False
        for sound in self.sounds:
            sound.pause()
            sound.disable()

    def update(self):
        subscription_result = traci.vehicle.getSubscriptionResults(self.id)
        position = subscription_result[tc.VAR_POSITION3D]
        angle = subscription_result[tc.VAR_ANGLE]
        speed = subscription_result[tc.VAR_SPEED]
        self.position = position
        self.angle = angle
        self.speed = speed
        self.update_sounds()

    def __del__(self):
        for sound in self.sounds:
            del sound


class PassengerVehicle(Vehicle):
    def __init__(self, id, engine_sound_file=_pkg_dir+"/stock_sounds/rally-car-idle-loop-17.wav",
                 tire_sound_file=_pkg_dir+"/stock_sounds/car-atspeed-loop.wav"):
        super().__init__(id)
        engine_sound = VehicleSound(engine_sound_file, base_gain=0.5)
        self.add_sound(engine_sound, "acceleration", [(0, 0.5), (2.5, 1)])
        tire_sound = VehicleSound(tire_sound_file, base_gain=2)
        self.add_sound(tire_sound, "speed", [(0, 0), (28, 1)])


class ElectricVehicle(Vehicle):
    def __init__(self, id, tire_sound_file=_pkg_dir+"/stock_sounds/car-atspeed-loop.wav"):
        super().__init__(id)
        tire_sound = VehicleSound(tire_sound_file, base_gain=1)
        self.add_sound(tire_sound, "speed", [(0, 0), (28, 1)])


class EmergencyVehicle(Vehicle):
    def __init__(self, id, engine_sound_file=_pkg_dir+"/stock_sounds/rally-car-idle-loop-17.wav",
                 tire_sound_file=_pkg_dir+"/stock_sounds/car-atspeed-loop.wav",
                 siren_sound_file=_pkg_dir+"/stock_sounds/siren-dutch-emergency-services.wav"):
        super().__init__(id)
        self.siren = True
        engine_sound = VehicleSound(engine_sound_file, base_gain=0.5)
        self.add_sound(engine_sound, "acceleration", [(0, 0.5), (2.5, 1)])
        tire_sound = VehicleSound(tire_sound_file, base_gain=2)
        self.add_sound(tire_sound, "speed", [(0, 0), (28, 1)])
        siren_sound = VehicleSound(siren_sound_file, base_gain=2)
        self.add_sound(siren_sound, "siren", [(False, 0), (True, 1)])


class Truck(Vehicle):
    def __init__(self, id, engine_sound_file=_pkg_dir+"/stock_sounds/truck-ext-idle-engine-close1.wav",
                 tire_sound_file=_pkg_dir+"/stock_sounds/car-atspeed-loop.wav"):
        super().__init__(id)
        engine_sound = VehicleSound(engine_sound_file, base_gain=2)
        self.add_sound(engine_sound, "acceleration", [(0, 0.5), (2.5, 1)])
        tire_sound = VehicleSound(tire_sound_file, base_gain=2)
        self.add_sound(tire_sound, "speed", [(0, 0), (28, 1)])


class Bicycle(Vehicle):
    def __init__(self, id, sound_file=_pkg_dir+"/stock_sounds/bicycle-ride.wav"):
        super().__init__(id)
        sound = VehicleSound(sound_file, base_gain=0.5)
        self.add_sound(sound, "speed", [(0, 0), (6, 1)])


if __name__ == "__main__":
    import time
    listener = oalGetListener()
    listener.set_position((0, -3, 0))
    listener.set_orientation((0, 1, 0, 0, 0, 0))
    listener.set_velocity((0, 0, 0))
    car1 = PassengerVehicle("car1")
    car1.enable()
    for i in range(-100, 100, 1):
        car1.position = (i, 0, 0)
        car1.speed = 10
        car1.angle = 90
        car1.update_sounds()
        time.sleep(0.1)
    oalQuit()
