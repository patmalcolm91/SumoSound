"""
Python library to generate sound effects for a Sumo traffic simulation using TraCI and PyOpenAL.

Author: Patrick Malcolm
"""

__all__ = ["Vehicle", "Sounds", "Ego", "Simulation"]
__version__ = "1.0.2"

import os
import sys

try:
    import traci
except ModuleNotFoundError:
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], '.')
        sys.path.append(tools)
        import traci
    else:
        raise ImportError("Could not import TraCI library. Please declare environment variable 'SUMO_HOME'.")

from .Vehicle import *
from .Sounds import *
from .Ego import *
from .Simulation import *
