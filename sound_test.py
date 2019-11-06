#!/usr/bin/python3

import os, sys
import time
import SumoSound

sys.path.append(os.getenv("SUMO_HOME"))
import traci

sumoBinary = "sumo-gui"
sumoCmd = [sumoBinary, "-c", "sound_test.sumocfg"]

soundEgo = SumoSound.Ego()
soundEgo.set_position((0, 0, 0))
soundEgo.set_angle(0)

soundSim = SumoSound.Simulation(soundEgo)

traci.start(sumoCmd)
step = 0
while step < 1000:
    traci.simulationStep()
    soundSim.update()
    step += 1
    time.sleep(0.1)

traci.close()
