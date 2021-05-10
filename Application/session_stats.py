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
        fileName = "data/comp_odds_by_" + str(b.id) + ".csv"
        with open(fileName, 'w', newline = '') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(b.oddsData)


def final_balances(bettingAgents):
    bettors = []
    for id, agent in bettingAgents.items():
        bettors.append(agent)

    header = []
    for i in range(len(bettors)):
        header.append(str(i))

    data = []
    for i in range(len(bettors)):
        data.append(bettors[i].balance)

    for b in bettors:
        fileName = "data/final_balance_" + str(b.id) + ".csv"
        with open(fileName, 'w', newline = '') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerow(data)



def createstats(bettingAgents):
    priv_bettor_odds(bettingAgents)
    final_balances(bettingAgents)
