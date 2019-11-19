"""
Classes and functions to handle a simulation.
"""

from .Ego import *
from .Vehicle import *
import traci
import traci.constants as tc
import warnings

DEFAULT_VEHICLE_CLASS_MAP = {
    "ignoring": PassengerVehicle,
    "private": PassengerVehicle,
    "emergency": EmergencyVehicle,
    "authority": PassengerVehicle,
    "army": Truck,
    "vip": PassengerVehicle,
    "pedestrian": None,
    "passenger": PassengerVehicle,
    "hov": Truck,
    "taxi": PassengerVehicle,
    "bus": Truck,
    "coach": PassengerVehicle,
    "delivery": Truck,
    "truck": Truck,
    "trailer": Truck,
    "motorcycle": PassengerVehicle,
    "moped": PassengerVehicle,
    "bicycle": Bicycle,
    "evehicle": ElectricVehicle,
    "tram": None,
    "rail_urban": None,
    "rail": None,
    "rail_electric": None,
    "rail_fast": None,
    "ship": None,
    "custom1": None,
    "custom2": None
}


class Simulation:
    def __init__(self, ego, vehicle_class_map=None, silent_ego=True, max_vehicle_count=None):
        """
        Initialize a Simulation object.
        Vehicle subclasses will be chosen based on the Sumo vClass of each vehicle.
        :param ego: Ego object
        :param vehicle_class_map: dict with Sumo vClass as keys and Vehicle subclass as values
        :param silent_ego: if True, the ego vehicle will not emit any sound.
        :param max_vehicle_count: maximum number of vehicles from which to emit sound. Vehicles closest to Ego are used.
        :type ego: Ego
        :type vehicle_class_map: dict[str: Vehicle]
        :type silent_ego: bool
        :type max_vehicle_count: int
        """
        self.ego = ego
        self.vehicles = dict()  # type: dict[str: Vehicle]
        self.vehicle_class_map = vehicle_class_map if vehicle_class_map is not None else DEFAULT_VEHICLE_CLASS_MAP
        self.silent_ego = silent_ego
        self.max_vehicle_count = max_vehicle_count

    def update(self):
        """
        This should be called every simulation timestep. Updates vehicle list and keeps vehicle sounds in sync with
        the Sumo simulation.
        :return: None
        """
        self.ego.update()
        vehicle_list = traci.vehicle.getIDList()
        # find newly added vehicles
        for vehID in vehicle_list:
            if self.silent_ego and hasattr(self.ego, "vehID") and vehID == self.ego.vehID:
                continue
            if vehID not in self.vehicles:
                self.add_vehicle(vehID, enabled=False)
        # update vehicles and find vehicles that have left the simulation
        to_remove = []
        for vehID in self.vehicles:
            if vehID not in vehicle_list:
                to_remove.append(vehID)
            else:
                self.vehicles[vehID].update()
        for vehID in to_remove:
            self.remove_vehicle(vehID)
        # enable relevant vehicles
        ex, ey, ez = self.ego.position
        veh_list = self.vehicles.values()
        distances = map(lambda v: ((v.position[0]-ex)**2+(v.position[1]-ey)**2)**0.5, veh_list)
        vehs_sorted = [v for (d, v) in sorted(zip(distances, veh_list), key=lambda p: p[0])]  # sort by distance
        for i, veh in enumerate(vehs_sorted):
            if self.max_vehicle_count is None or i <= self.max_vehicle_count:
                if not veh.enabled:
                    try:
                        veh.enable()
                    except al.ALError:
                        self.max_vehicle_count = i-1
                        warnings.warn("Failed to add vehicle. Setting max vehicle count to " + str(i-1), RuntimeWarning)
            else:
                if veh.enabled:
                    veh.disable()

    def add_vehicle(self, vehID, enabled=True):
        """
        Adds the vehicle with the specified id to the Simulation. The vehicle settings are chosen based on its vClass.
        :param vehID: id of the Sumo vehicle
        :param enabled: whether or not the vehicle should be enabled by default
        :return: None
        :type vehID: str
        :type enabled: bool
        """
        vClass = traci.vehicle.getVehicleClass(vehID)
        if vClass in self.vehicle_class_map and self.vehicle_class_map[vClass] is not None:
            vehicle = self.vehicle_class_map[vClass](vehID)
            if enabled:
                vehicle.enable()
            self.vehicles[vehID] = vehicle

    def remove_vehicle(self, vehID):
        """
        Remove the vehicle with the specified id from the simulation.
        :param vehID:
        :return: None
        :type vehID: str
        """
        self.vehicles[vehID].disable()
        del self.vehicles[vehID]

    def __del__(self):
        oalQuit()
