"""
Classes and functions for defining and controlling the ego.
"""

import math
from openal import *
import traci
import traci.constants as tc
from typing import Union, List, Tuple

_ego_declared = False


class Ego:
    """
    Simple Ego for listening at a fixed point or to be manually moved around by script.
    Custom Ego classes should subclass this class.
    """
    def __init__(self):
        global _ego_declared
        if _ego_declared:
            raise UserWarning("Multiple Egos created. This could have undesired effects.")
        self.listener = oalGetListener()  # type: Listener
        self.position = (0, 0, 0)
        self.velocity = (0, 0, 0)
        self.orientation = (0, 0, 0, 0, 0, 0)
        _ego_declared = True

    def set_position(self, position):
        """
        Sets position of the Ego.
        :param position: 3-component position vector.
        :return: None
        :type position: Tuple[float, float, float]
        """
        self.position = position
        self.listener.set_position(position)

    def set_velocity(self, velocity):
        """
        Sets velocity vector of the Ego.
        :param velocity: 3-component velocity vector.
        :return: None
        :type velocity: Tuple[float, float, float]
        """
        self.velocity = velocity
        self.listener.set_velocity(velocity)

    def set_orientation(self, orientation):
        """
        Sets sound orientation from orientation vector.
        :param orientation: 6-component orientation vector. See OpenAL documentation.
        :return: None
        :type orientation: Tuple[float, float, float, float, float, float]
        """
        self.orientation = orientation
        self.listener.set_orientation(orientation)

    def set_angle(self, angle):
        """
        Sets orientation of Ego from geographic angle.
        :param angle: Geographic angle (CW from North) [deg]
        :return: None
        :type angle: float
        """
        geometric_angle = ((360 - angle + 90) % 360) * math.pi / 180
        ox = math.cos(geometric_angle)
        oy = math.sin(geometric_angle)
        self.set_orientation((ox, oy, 0, 0, 0, 0))

    def set_master_volume(self, gain):
        """
        Sets the gain of the Ego, effectively adjusting the master volume of all sounds in the simulation.
        :param gain: Desired gain (0-inf)
        :return: None
        """
        self.listener.set_gain(gain)

    def update(self):
        """Function which will be called every timestep. To be overridden by subclasses as needed."""
        pass


class EgoVehicle(Ego):
    """
    Normal Sumo Ego Vehicle. The position, orientation, and speed are pulled directly from TraCI.
    """
    def __init__(self, vehID, listener_offset=(0, 0, 1.8)):
        """
        Initializes an EgoVehicle object.
        :param vehID: Sumo vehicle ID with which to sync.
        :param listener_offset: offset vector from vehicle position to listener position
        :type vehID: str
        :type listener_offset: Tuple[float, float, float]
        """
        super().__init__()
        self.vehID = vehID
        self.subscribed = False
        vehicle_list = traci.vehicle.getIDList()
        if self.vehID in vehicle_list:
            self.subscribe()
            self.subscribed = True
        self.position = (0, 0, 0)
        self.listener_offset = listener_offset
        self.angle = 0
        self.speed = 0

    def subscribe(self):
        """Adds a TraCI subscription for the ego vehicle"""
        traci.vehicle.subscribe(self.vehID, (tc.VAR_POSITION3D, tc.VAR_ANGLE, tc.VAR_SPEED))

    def get_velocity_vector(self):
        """Calculates the velocity vector of the Ego vehicle."""
        return [self.speed*i for i in self.get_orientation_vector()]

    def get_orientation_vector(self):
        """Calculates the first three components of the OpenAL orientation vector of the Ego vehicle."""
        geometric_angle = ((360 - self.angle + 90) % 360) * math.pi / 180
        ox = math.cos(geometric_angle)
        oy = math.sin(geometric_angle)
        return [ox, oy, 0]

    def update(self):
        """
        Polls vehicle subscription data from TraCI and updates the vehicle accordingly.
        Should be run every simulation step.
        :return: None
        """
        if not self.subscribed:
            vehicle_list = traci.vehicle.getIDList()
            if self.vehID in vehicle_list:
                self.subscribe()
            else:
                return
        subscription_result = traci.vehicle.getSubscriptionResults(self.vehID)
        position = subscription_result[tc.VAR_POSITION3D]
        angle = subscription_result[tc.VAR_ANGLE]
        speed = subscription_result[tc.VAR_SPEED]
        self.position = position
        self.angle = angle
        self.speed = speed
        self._set_listener_properties()

    def _set_listener_properties(self):
        """
        Sets the OpenAL Listener properties based on the Ego Vehicle's current state.
        :return:
        """
        listener_position = tuple([self.position[i] + self.listener_offset[i] for i in range(len(self.position))])
        self.listener.set_position(listener_position)
        self.listener.set_velocity(self.get_velocity_vector())
        self.listener.set_orientation(self.get_orientation_vector() + [0, 0, 0])


class EgoVehicleManualSpeed(EgoVehicle):
    """
    Sumo Ego Vehicle in which only position and angle are pulled from TraCI,
    but speed is calculated manually from the positions. This is useful if the vehicle is not being controlled directly
    by Sumo, but from an external script or program, in which case the speed value in Sumo is not correctly reported.
    """
    def __init__(self, vehID, listener_offset=(0, 0, 1.8)):
        """
        Initializes an EgoVehicleManualSpeed object.
        :param vehID: Sumo vehicle ID with which to sync.
        :param listener_offset: offset vector from vehicle position to listener position
        :type vehID: str
        :type listener_offset: Tuple[float, float, float]
        """
        super().__init__(vehID, listener_offset)
        self.last_position = None

    def update(self):
        """
        Polls vehicle subscription data from TraCI and updates the vehicle accordingly.
        Should be run every simulation step.
        :return: None
        """
        if not self.subscribed:
            vehicle_list = traci.vehicle.getIDList()
            if self.vehID in vehicle_list:
                self.subscribe()
            else:
                return
        subscription_result = traci.vehicle.getSubscriptionResults(self.vehID)
        position = subscription_result[tc.VAR_POSITION3D]
        angle = subscription_result[tc.VAR_ANGLE]
        self.position = position
        self.angle = angle
        if self.last_position is not None:
            x0, y0, z0 = self.last_position
            x1, y1, z1 = self.position
            self.speed = math.sqrt((x1-x0)**2 + (y1-y0)**2 + (z1-z0)**2)
        else:
            self.speed = 0
        self.last_position = position
        self._set_listener_properties()


if __name__ == "__main__":
    pass
