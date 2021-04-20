import sys, math, threading, time, queue, random, csv, config
from copy import deepcopy
from system_constants import *
from betting_agents import *
from race_simulator import Simulator
from ex_ante_odds_generator import *
from exchange import Exchange
from message_protocols import *
from session_stats import *

def main():
    # Simulation attributes
    currentSimulation = 0
    numOfSimulations = 1
    ####################

    # set things up
    # have while loop for running multiple races
    # within loop instantiate competitors into list
    # run simulation and matching engine
    while currentSimulation < NUM_OF_SIMS:
        simulationId = "Simulation: " + str(currentSimulation)

        # Create race event data
        race = Simulator(NUM_OF_COMPETITORS)
        compPool = deepcopy(race.competitors)
        raceAttributes = deepcopy(race.race_attributes)
        raceFilename = str(currentSimulation)

        race.run(raceFilename)

        currentSimulation = currentSimulation + 1






if __name__ == "__main__":
    main()
