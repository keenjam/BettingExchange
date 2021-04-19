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

index = 0
agents = {}
exAnteOdds = {}
adaptedCompPools = {}
raceAttributes = None

def createAdaptedCompPools(compPool, numOfPriveledgedBettors):
    disturbances = []
    for i in range(1, numOfPriveledgedBettors+1):
        disturbances.append((0.1*numOfPriveledgedBettors) / i)

    adaptedViewOfCompPool = deepcopy(compPool)
    for i in range(numOfPriveledgedBettors):
        pool = deepcopy(adaptedViewOfCompPool)
        for c in pool:
            c.alignment = c.alignment + (random.uniform(-disturbances[i], disturbances[i]))
        adaptedCompPools[i] = pool


def createOdds(index, compPool, numOfSimulations, raceState = None):
    pool = deepcopy(compPool)
    if raceState != None:
        for c in pool:
            c.distance = float(raceState[c.id])

    oddsOfWinning = [0] * len(compPool)

    for j in range(numOfSimulations):
        p  = deepcopy(pool)
        j = Simulator(NUM_OF_COMPETITORS, p, raceAttributes)
        j.run(None)
        oddsOfWinning[j.winner] = oddsOfWinning[j.winner] + 1
    #print(oddsOfWinning)
    for i in range(len(oddsOfWinning)):
        if oddsOfWinning[i] == 0: oddsOfWinning[i] = MAX_ODDS
        else:
            p = (oddsOfWinning[i] / numOfSimulations) * 100
            oddsOfWinning[i] = 100 / p
    #print(oddsOfWinning)
    #oddsOfWinning[:] = [(100 / (o / numOfSimulations)) for o in oddsOfWinning]
    if raceState != None:
        return oddsOfWinning
    else:
        exAnteOdds[index] = oddsOfWinning

def createExAnteOdds(compPool, attributes):
    global raceAttributes
    raceAttributes = attributes
    numOfPriveledgedBettors = 0
    for agent in config.agents:
        type = agent[0]
        if type == 'Priveledged':
            numOfPriveledgedBettors = agent[1]
            break
    createAdaptedCompPools(compPool, numOfPriveledgedBettors)
    for i in range(numOfPriveledgedBettors):
        createOdds(i, adaptedCompPools[i], 20)


def getExAnteOdds(agentId):
    global index
    agents[agentId] = index
    index = index + 1
    print(index)
    return exAnteOdds[agents[agentId]]

def getInPlayOdds(agentId, raceState):
    i = agents[agentId]
    pool = deepcopy(adaptedCompPools[i])
    return createOdds(i, pool, 20, raceState)






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
