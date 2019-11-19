# SumoSound
SumoSound is a Python package which uses Sumo's TraCI API and PyOpenAL to generate
vehicle sounds in a 3D environment. PyOpenAL calculates the proper volume, doppler
shift, and stereo (or surround sound) output. The package comes with some built-in 
default sound effects, but is fully customizable, and can calculate the sounds from
the point of view of either a stationary ego position or one of the vehicles in the
simulation.

## Installation
SumoSound can be installed using pip:
```
pip install SumoSound
```

Or, you can simply clone the GitHub repository and add it to your Python path.

You can then import the library.
```python
import SumoSound
```

### Dependencies
* Sumo TraCI
* PyOpenAL

## Usage
See the example script [sound_test.py](sound_test.py) for an example.

In general, you just need to define an ```Ego``` object (either of the ```Ego``` class or a
subclass of it), pass this ```Ego``` object to a ```Simulation``` object, and then call 
```update()``` on the ```Simulation``` object once per simulation step. Everything else 
should be handled automatically.

## Documentation

### Ego
An ```Ego``` object defines the position, velocity, and orientation of the listener.
There are 3 ego types: Stationary Ego, Ego Vehicle, and Ego Vehicle with Manually-Calculated Speed.

#### Stationary Ego (```Ego```)
The position, velocity, and orientation of a stationary ego are controlled with the methods ```set_position()```,
```set_velocity()```, and ```set_angle()```. The ego will default to a location of (0, 0, 0) facing east with
zero velocity.
```python
ego = SumoSound.Ego()
```

#### Ego Vehicle (```EgoVehicle```)
The position, velocity, and orientation of an ego vehicle are synced via TraCI with the vehicle with the given ID.
These properties are automatically updated every time step by the ```Simulation``` object.
```python
ego = SumoSound.EgoVehicle("vehicleID")
```

#### Ego Vehicle with Manually-Calculated Speed (```EgoVehicleManualSpeed```)
The same as an ```EgoVehicle```, but the vehicle speed is calculated based on the ego position in the previous and
current simulation time steps. This is useful if the ego vehicle is being controlled externally and the speed property
is incorrect or undefined.
```python
ego = SumoSound.EgoVehicleManualSpeed("vehicleID")
```

### Simulation
A ```Simulation``` object keeps track of all of the vehicles in the Sumo simulation via TraCI, updating the sound
sources and listener position as necessary. An ego must be passed to the constructor of the ```Simulation``` object.
```python
simulation = SumoSound.Simulation(ego)
```
Additional parameters are available as well. Most notably, the argument ```vehicle_class_map``` can be used to tell
SumoSound which subclass of ```Vehicle``` to use for each Sumo vehicleClass. By default, the dict
```DEFAULT_VEHICLE_CLASS_MAP``` is used. For more information on defining custom vehicle types, see the next section.

The method ```update()``` must be called every simulation step.
```python
while True:
    traci.simulationStep()
    simulation.update()
```

### Vehicle
A ```Vehicle``` object keeps track of one or more sound sources associated with the vehicle type. SumoSound comes with a
number of pre-defined vehicle types which are selected automatically by the ```Simulation``` object based on the Sumo
vehicleClass property of each vehicle. Custom vehicle types can be created by simply sub-classing the ```Vehicle```
class. The gain of each vehicle sound can be automatically actuated by a signal. By default, the speed and acceleration
of the vehicle are available as signals, but custom signals can also be created.

```python
class CustomVehicle(SumoSound.Vehicle):
    def __init__(self, id, engine_sound_file="path/to/file.wav",
                 tire_sound_file="path/to/file.wav",
                 horn_sound_file="path/to/file.wav"):
        super().__init__(id)
        self.horn = False  # define a custom signal called "horn"
        # add an engine sound to the vehicle, actuated by the vehicle acceleration
        engine_sound = SumoSound.VehicleSound(engine_sound_file, base_gain=0.5)
        self.add_sound(engine_sound, "acceleration", response_curve=[(0, 0.5), (2.5, 1)])
        # add a tire sound to the vehicle, actuated by the vehicle speed
        tire_sound = SumoSound.VehicleSound(tire_sound_file, base_gain=2)
        self.add_sound(tire_sound, "speed", response_curve=[(0, 0), (28, 1)])
        # add a horn sound to the vehicle, actuated by the custom signal "horn"
        horn_sound = SumoSound.VehicleSound(horn_sound_file, base_gain=2)
        self.add_sound(horn_sound, "horn", response_curve=[(False, 0), (True, 1)])
```

The argument ```response_curve``` of the method ```add_sound()``` may either be a callable with the signature
```fun(signal_value) -> gain``` or a list of ```(signal_value, gain)``` tuples, which are interpolated as necessary to
calculate the sound gain from the signal value.

To associate the custom vehicle type with a vehicle class, the ```vehicle_class_map``` argument of the ```Simulation```
constructor must be passed a custom dict containing the desired mapping, or the default dict can be modified before
creating the Simulation object.
```python
# map the custom vehicle type to the Sumo vehicleClass "passenger"
SumoSound.DEFAULT_VEHICLE_CLASS_MAP["passenger"] = CustomVehicle
simulation = SumoSound.Simulation(ego)
```

In order to use the custom signal to actuate the sound, simply set the signal to the desired value, and everything will
be automatically handled the next time the simulation is updated.
```python
simulation.vehicles["vehicleID"].horn = True
```

## Contribution
Issues and pull requests are welcome.