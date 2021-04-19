import sys, math, threading, time, queue, random, csv, config, random, operator
from message_protocols import Order
from system_constants import *
from ex_ante_odds_generator import getExAnteOdds, getInPlayOdds





def priv_bettor_odds(bettingAgents):
    privBettors = []
    for id, agent in bettingAgents.items():
        if agent.name == 'Priveledged': privBettors.append(agent)

    # oddsdata = {}
    # for b in privBettors:
    #     oddsdata[b.id] = b.oddsData

    header = ["Time"]
    for c in range(NUM_OF_COMPETITORS):
        header.append(str(c))

    for b in privBettors:
        fileName = "comp_odds_by_" + str(b.id) + ".csv"
        print(b.oddsData)
        with open(fileName, 'w', newline = '') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(b.oddsData)










def createstats(bettingAgents):
    priv_bettor_odds(bettingAgents)
