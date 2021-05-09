### CREATE EX-ANTE ODDS FOR PRIVELEDGED BETTORS BY RUNNING MULTIPLE SOLUTIONS ###

import sys, math, threading, time, queue, random, csv, config
import numpy as np
from copy import deepcopy
from system_constants import *
from betting_agents import *
from race_simulator import Simulator
from exchange import Exchange
from message_protocols import *

'''

To most accurately simulate the precense of priveledged bettors in the market
will take competitors alignment (between [0,1]) to race preferences and randomely alter it
within a range (0 -> i) where i reduces inversely to num of priveledged bettors
e.g for bettor one i is large for bettor n i is v small such that that bettor
will have an almost omniscient view of the race.

In play events and the stochastic events that will occur during its course will
still be representative of how even having priveledged info doesn't garuantee
betting success

'''

agents = {}
exAnteOdds = {}
inPlayOdds = {}
adaptedCompPools = {}
raceAttributes = None
NUM_OF_PRIV_BETTORS = 0


def observeRace(timestep):
    with open(RACE_DATA_FILENAME, 'r') as file:
        reader = csv.reader(file)
        r = [row for index, row in enumerate(reader) if index == timestep]
    time = r[0][0]
    compDistances = {}
    for c in range(NUM_OF_COMPETITORS):
        compDistances[c] = float(r[0][c+1])

    return compDistances

def createAdaptedCompPools(compPool, numOfPriveledgedBettors):
    disturbances = []
    for i in range(1, numOfPriveledgedBettors+1):
        disturbances.append((0.05*numOfPriveledgedBettors) / i)

    adaptedViewOfCompPool = deepcopy(compPool)
    for i in range(numOfPriveledgedBettors):
        pool = deepcopy(adaptedViewOfCompPool)
        for c in pool:
            c.alignment = c.alignment + (random.uniform(-disturbances[i], disturbances[i]))
        adaptedCompPools[i] = pool


def createOdds(ix, compPool, numOfSimulations, timestep = None, raceState = None):
    global raceAttributes
    pool = deepcopy(compPool)
    if raceState != None:
        raceLen = raceAttributes.length
        for c in pool:
            c.distance = float(raceState[c.id])

    oddsOfWinning = [0] * len(compPool)

    for j in range(numOfSimulations):
        p  = deepcopy(pool)
        for c in p:
            c.consistency = random.gauss(1, 0.1)
        j = Simulator(NUM_OF_COMPETITORS, p, raceAttributes)
        j.run(None)
        oddsOfWinning[j.winner] = oddsOfWinning[j.winner] + 1
    #print(oddsOfWinning)
    for i in range(len(oddsOfWinning)):
        if oddsOfWinning[i] == 0: oddsOfWinning[i] = MAX_ODDS
        else:
            p = (oddsOfWinning[i] / numOfSimulations)
            oddsOfWinning[i] =  1 / p
            if oddsOfWinning[i] > MAX_ODDS: oddsOfWinning[i] = MAX_ODDS
    #print(oddsOfWinning)
    #oddsOfWinning[:] = [(100 / (o / numOfSimulations)) for o in oddsOfWinning]
    if raceState != None and timestep != None:
        if timestep not in inPlayOdds:
            inPlayOdds[timestep] = [oddsOfWinning]
        else:
            inPlayOdds[timestep].append(oddsOfWinning)
    else:
        exAnteOdds[ix] = oddsOfWinning



def createExAnteOdds(compPool, attributes):
    global raceAttributes
    global NUM_OF_PRIV_BETTORS
    raceAttributes = attributes
    numOfPriveledgedBettors = 0
    for agent in config.agents:
        type = agent[0]
        if type == 'Priveledged':
            numOfPriveledgedBettors = agent[1]
            break
    NUM_OF_PRIV_BETTORS = numOfPriveledgedBettors
    createAdaptedCompPools(compPool, numOfPriveledgedBettors)
    for i in range(numOfPriveledgedBettors):
        createOdds(i, adaptedCompPools[i], 10)



def createInPlayOdds(numberOfTimesteps):
    numOfPriveledgedBettors = 0
    for agent in config.agents:
        type = agent[0]
        if type == 'Priveledged':
            numOfPriveledgedBettors = agent[1]
            break

    for t in range(numberOfTimesteps):
        print(t)
        for i in range(numOfPriveledgedBettors):
            raceState = observeRace(t)
            print(raceState)
            pool = deepcopy(adaptedCompPools[i])

            createOdds(i, pool, 10, t, raceState)




# Getter functions for betting agents

def getExAnteOdds(agentId):
    global agents
    # agent id is is agentid % NUM OF PRIVELEDGED BETTORS
    agents[agentId] = agentId % NUM_OF_PRIV_BETTORS
    # index = index + 1
    #print(str(agentId) + " " + str(agents[agentId]))
    return exAnteOdds[agents[agentId]]

def getInPlayOdds(timestep, agentId):
    odds = inPlayOdds[timestep]
    return odds[agents[agentId]]







# def createExAnteOdds(compPool):
#     print("BANG BANG")
#     numOfSimulations = 100
#     numOfPriveledgedBettors = 0
#     for agent in config.agents:
#         type = agent[0]
#         if type == 'Priveledged':
#             numOfPriveledgedBettors = agent[1]
#             break
#
#     disturbances = []
#     for i in range(1, numOfPriveledgedBettors+1):
#         disturbances.append((0.1*numOfPriveledgedBettors) / i)
#
#     adaptedViewOfCompPool = deepcopy(compPool)
#
#     for i in range(numOfPriveledgedBettors):
#         pool = deepcopy(adaptedViewOfCompPool)
#         for c in pool:
#             c.alignment = c.alignment + (random.uniform(-disturbances[i], disturbances[i]))
#         oddsOfWinning = [0] * len(compPool)
#
#         for j in range(numOfSimulations):
#             p  = deepcopy(pool)
#             j = Simulator(NUM_OF_COMPETITORS, p)
#             j.run(None)
#             #print(j.winner)
#             oddsOfWinning[j.winner] = oddsOfWinning[j.winner] + 1
#         oddsOfWinning[:] = [o / len(compPool) for o in oddsOfWinning]
#         print(oddsOfWinning)
#         exAnteOdds.append(oddsOfWinning)

#
# def getExAnteOdds():
#     global index
#     odds = exAnteOdds[index]
#     index = index + 1
#     print("INDEX: " + str(index))
#     return odds
