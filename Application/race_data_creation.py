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
    numOfSimulations = 5000
    ####################

    # set things up
    # have while loop for running multiple races
    # within loop instantiate competitors into list
    # run simulation and matching engine
    avgtime = 0
    faveWinPercentage = 0

    horseByOdds = []
    better = []
    worse = []
    same = []
    for i in range(8):
        horseByOdds.append(0)
        better.append(0)
        worse.append(0)
        same.append(0)



    while currentSimulation < numOfSimulations:
        simulationId = "Simulation: " + str(currentSimulation)

        # Create race event data
        race = Simulator(8)
        compPool = deepcopy(race.competitors)
        raceAttributes = deepcopy(race.race_attributes)
        raceFilename = str(currentSimulation)
        s = time.time()

        createExAnteOdds(compPool, raceAttributes)

        race.run(raceFilename)
        e = time.time()
        avgtime = avgtime + (e-s)

        exAnteOdds = getExAnteOdds(38)
        # minOdds = min(exAnteOdds)
        # c = exAnteOdds.index(minOdds)
        # print(exAnteOdds)

        exAnteOdds = sorted(range(len(exAnteOdds)), key=lambda k: exAnteOdds[k])


        for i in range(len(exAnteOdds)):
            print(str(exAnteOdds[i]) + " : " + str(race.finished.index(exAnteOdds[i])) +  " : " + str(i))
            if race.finished.index(exAnteOdds[i]) < i:
                better[i] += 1
                print("bettor")
            elif race.finished.index(exAnteOdds[i]) > i:
                worse[i] += 1
                print("worse")
            elif race.finished.index(exAnteOdds[i]) == i:
                same[i] += 1
                print("same")
            if race.winner == exAnteOdds[i]:
                horseByOdds[i] += 1


        #
        # if c == race.winner:
        #     faveWinPercentage += 1



        currentSimulation = currentSimulation + 1

    print(avgtime / currentSimulation)
    print(horseByOdds)
    for i in range(len(horseByOdds)):
        horseByOdds[i] /= numOfSimulations
        better[i] /= numOfSimulations
        worse[i] /= numOfSimulations
        same[i] /= numOfSimulations

    print(horseByOdds)
    print(better)
    print(worse)
    print(same)





if __name__ == "__main__":
    main()
