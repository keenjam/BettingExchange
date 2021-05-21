import sys, math, threading, time, queue, random, csv, config, random, operator
from message_protocols import Order
from system_constants import *
from ex_ante_odds_generator import getExAnteOdds, getInPlayOdds


def recordPrices(timestep, exchanges, record):
    for id, ex in exchanges.items():
        compData = {}
        for orderbook in ex.compOrderbooks:
            ob = orderbook.backs.bestOdds
            ol = orderbook.lays.bestOdds

            if(ob == None and ol == None):
                compData[orderbook.competitorId] = MAX_ODDS
            elif(ob == None):
                compData[orderbook.competitorId] = ol
            elif(ol == None):
                compData[orderbook.competitorId] = ob
            else:
                print(ob)
                print(ol)
                print(orderbook.backs.market)
                print("BANG")
                print(orderbook.lays.market)
                qtyB = orderbook.backs.market[ob][0]
                qtyL = orderbook.lays.market[ol][0]

                microprice = ((ob * qtyL) + (ol * qtyB)) / (qtyB + qtyL)
                #if ob == None: ob = MAX_ODDS
                compData[orderbook.competitorId] = microprice

        record[timestep] = compData

def recordSpread(timestep, exchanges, record):
    for id, ex in exchanges.items():
        compData = {}
        for orderbook in ex.compOrderbooks:
            ob = orderbook.backs.bestOdds
            ol = orderbook.lays.bestOdds


            # if(ob == None and ol == None):
            #     compData[orderbook.competitorId] = None
            # elif(ob == None):
            #     compData[orderbook.competitorId] = None
            # elif(ol == None):
            #     compData[orderbook.competitorId] = None
            if(ob != None and ol != None):
                spread = abs((1/ob) - (1/ol))
                #if ob == None: ob = MAX_ODDS
                if spread != 0:
                    compData[orderbook.competitorId] = spread

        record[timestep] = compData

def price_histories(priceHistory, simId):
    history = []
    for id, items in priceHistory.items():
        history.append(items)

    rows = [ [k] + [ (MAX_ODDS if (z == None) else z) for c, z in v.items() ] for k, v in priceHistory.items() ]

    header = ["Time"]
    for c in range(NUM_OF_COMPETITORS):
        header.append(str(c))

    # print(priceHistory)
    print(rows)

    fileName = "data/price_histories_" + str(simId) + ".csv"
    with open(fileName, 'w', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)

def price_spread(spreadHistory, simId):

    rows = [ [k] + [ (MAX_ODDS if (z == None) else z) for c, z in v.items() ] for k, v in spreadHistory.items() ]

    header = ["Time"]
    for c in range(NUM_OF_COMPETITORS):
        header.append(str(c))

    # print(priceHistory)
    print(rows)

    fileName = "data/price_spreads_" + str(simId) + ".csv"
    with open(fileName, 'w', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


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


def final_balances(bettingAgents, simId):
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
        fileName = "data/final_balance_" + str(simId) + "_" + str(b.id) + ".csv"
        with open(fileName, 'w', newline = '') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerow(data)


def transactions(trades, simId):
    header = ["type", "time", "exchange", "competitor", "odds", "backer", "layer", "stake"]
    tape = []
    for val in trades:
        temp = []
        for i, v in val.items():
            temp.append(v)
        tape.append(temp)


    fileName = "data/transactions_" + str(simId) + ".csv"
    with open(fileName, 'w', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(tape)



def createstats(bettingAgents, simId, trades, priceHistory, spreadHistory):
    priv_bettor_odds(bettingAgents)
    final_balances(bettingAgents, simId)
    price_histories(priceHistory, simId)
    price_spread(spreadHistory, simId)
    transactions(trades, simId)
