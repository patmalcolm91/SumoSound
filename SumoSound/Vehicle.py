"""
Contains Vehicle classes and related classes and functions.
"""

import os
from .Sounds import *
import math
import traci
import traci.constants as tc
import shapely.geometry
import shapely.ops
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

    @staticmethod
    def _calculate_response_from_curve(curve, x):
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

    def update_custom_signals(self):
        """Override this method to add custom signal-updating logic. Called by update() before update_sounds()."""
        pass

    def update(self):
        subscription_result = traci.vehicle.getSubscriptionResults(self.id)
        position = subscription_result[tc.VAR_POSITION3D]
        angle = subscription_result[tc.VAR_ANGLE]
        speed = subscription_result[tc.VAR_SPEED]
        self.position = position
        self.angle = angle
        self.speed = speed
        self.update_custom_signals()
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
        siren_sound = VehicleSound(siren_sound_file, base_gain=2, random_pos=False)
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


class RailVehicle(Vehicle):
    def __init__(self, id, sound_file, base_gain=1):
        super().__init__(id)
        # create variables for storing traversed lanes, used to calculate train shape (not currently available in TraCI)
        self.traversed_lanes = []
        self._traversed_lanes_alignment = None
        self._current_lane_length = None
        # get positions of carriages along train alignment
        vType = traci.vehicle.getTypeID(self.id)
        carriage_length = traci.vehicletype.getParameter(vType, "carriageLength")
        self.carriage_length = float(carriage_length) if carriage_length is not "" else 16.75
        locomotive_length = traci.vehicletype.getParameter(vType, "locomotiveLength")
        self.locomotive_length = float(locomotive_length) if locomotive_length is not "" else 16.75
        carriage_gap = traci.vehicletype.getParameter(vType, "carriageGap")
        self.carriage_gap = float(carriage_gap) if carriage_gap is not "" else 0
        self.length = traci.vehicle.getLength(self.id)
        self.carriage_positions = [self.locomotive_length/2]
        pos = self.carriage_positions[0] + self.carriage_length + self.carriage_gap
        while pos < self.length:
            self.carriage_positions.append(pos)
            pos += self.carriage_length + self.carriage_gap
        # add one sound per carriage
        for p in self.carriage_positions:
            sound = VehicleSound(sound_file, base_gain=base_gain)
            self.add_sound(sound, "speed", [(0, 0), (35, 1)])
        self.update_custom_signals()

    def _get_vehicle_shape(self):
        """return the shape of the train as a shapely LineString"""
        current_lane = traci.vehicle.getLaneID(self.id)
        lane_pos = traci.vehicle.getLanePosition(self.id)
        if len(self.traversed_lanes) == 0 or self.traversed_lanes[-1] != current_lane:
            self.traversed_lanes.append(current_lane)
            self._current_lane_length = traci.lane.getLength(current_lane)
            lane_coords = traci.lane.getShape(current_lane)
            lane_align = shapely.geometry.LineString(lane_coords)
            if self._traversed_lanes_alignment is None:
                self._traversed_lanes_alignment = lane_align
            else:
                self._traversed_lanes_alignment = shapely.ops.linemerge([self._traversed_lanes_alignment, lane_align])
        vehicle_shape = shapely.ops.substring(self._traversed_lanes_alignment, -self._current_lane_length+lane_pos,
                                              -self._current_lane_length+lane_pos-self.length)
        return vehicle_shape

    def update_custom_signals(self):
        # instead of calculating signal values, adjust sound relative positions based on train shape
        vehicle_shape = self._get_vehicle_shape()
        positions = [tuple(shapely.ops.substring(vehicle_shape, pos, pos).coords[0]) for pos in self.carriage_positions]
        for i, sound in enumerate(self.sounds):
            abs_pos = (positions[i][0], positions[i][1], self.position[2])
            rel_pos = tuple([abs_pos[i]-self.position[i] for i in range(3)])
            sound.relative_position = rel_pos


class HeavyRailVehicle(RailVehicle):
    def __init__(self, id, sound_file=_pkg_dir+"/stock_sounds/freight_train.wav"):
        super().__init__(id, sound_file=sound_file, base_gain=2)


class HighSpeedRailVehicle(RailVehicle):
    def __init__(self, id, sound_file=_pkg_dir+"/stock_sounds/high-speed-train.wav"):
        super().__init__(id, sound_file=sound_file, base_gain=3)


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
