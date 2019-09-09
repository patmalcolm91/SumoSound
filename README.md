# SumoSound
SumoSound is a Python package which uses Sumo's TraCI API and PyOpenAL to generate
vehicle sounds in a 3D environment. It comes with some built-in default sound effects,
but is fully customizable, and can calculate the sounds from the point of view of
either a stationary ego position or one of the vehicles in the simulation.

## Installation
Simply clone this repository and add it to your Python path. You can then import
the library
```python
import SumoSound
```

### Dependencies
* Sumo TraCI
* PyOpenAL

## Usage
See the example script ```sound_test.py``` for an example. Further documentation
is forthcoming.

In general, you just need to define an Ego object (either of the Ego class or a
subclass of it), pass this Ego object to a Simulation object, and then call update()
on the Simulation object once per simulation step. Everything else should be handled
automatically.

## Contribution
Issues and pull requests are welcome.