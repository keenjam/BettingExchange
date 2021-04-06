### ~ THREADED BRISTOL BETTING EXCHANGE ~ ###

'''
Page 56 - The Perfect Bet
Strategy by Benter -> Find predicted odds then combine with markets as markets may contain privileged infomation

Should be stock pool of betting agents representing normal civilian bettors (eg. with range from less to more privileged info - recreational and insiders (eg. knowing diet / jockey strat))


'''



import sys, math, threading, time, queue, random, csv, config, random
from message_protocols import Order
from system_constants import *

class BettingAgent:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.balance = 500
        self.availableBalance = self.balance
        self.orders = {}
        self.numOfBets = 0 # Number of bets live on BBE

    def observeRaceState(self, timestep, compDistances):
        # print(str(self.id) + " observed race with")
        # print(compDistances)
        return None

    def bookkeep(self, trade, order, time):
        self.numOfBets = self.numOfBets - 1
        self.availableBalance = self.availableBalance - order.stake
        return None

    def respond(self, time, markets, trade):
        return None

class Agent_Random(BettingAgent):
    def getorder(self, time, markets):
        r = random.randint(0,1)
        if(r == 0):
            c = random.randint(0, NUM_OF_COMPETITORS-1)
            e = random.randint(0, NUM_OF_EXCHANGES-1)
            minodds = 5
            maxodds = 6
            b = random.randint(0,1)
            if(b == 0):
                quoteodds = random.randint(minodds, minodds + 3)
                order = Order(e, self.id, c, 'Back', quoteodds, markets[e][c]['QID'], 1, time)
                print("BACK MADE BY AGENT " + str(self.id))
            else:
                quoteodds = random.randint(maxodds - 3, maxodds)
                order = Order(e, self.id, c, 'Lay', quoteodds, markets[e][c]['QID'], 1, time)
                print("LAY MADE BY AGENT " + str(self.id))
        else:
            order = None

        return order



class Agent_Test(BettingAgent):
    def hello():
        print("Hello World")

        # self.exchange = exchange
        # self.agentId = agentId
        # self.competitorId = competitorId
        # self.direction = direction
        # self.odds = odds
        # self.stake = stake
        # self.orderId = orderId
        # self.timestamp = time

    def getorder(self, time, markets):
        order = None
        if self.numOfBets < 1 and self.id == 0:
            order = Order(0, self.id, 0, 'Back', 10.0, 1, 1, time)

        elif self.numOfBets < 1 and self.id == 1:
            order = Order(0, self.id, 0, 'Lay', 9.0, 1, 1, time)

        return order
