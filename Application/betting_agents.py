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
    def __init__(self, id, name, exchange = None):
        self.id = id
        self.name = name
        self.balance = 500
        self.availableBalance = self.balance
        self.orders = {}
        self.numOfBets = 0 # Number of bets live on BBE
        self.exchange = 0

        # race details
        self.raceStarted = False
        self.raceTimestep = 0
        self.currentRaceState = {}

    def observeRaceState(self, timestep, compDistances):
        if self.raceStarted == False: self.raceStarted = True
        for id, dist in compDistances.items():
            self.currentRaceState[id] = dist
        self.raceTimestep = int(timestep)

    def bookkeep(self, trade, order, time):
        self.numOfBets = self.numOfBets - 1
        self.availableBalance = self.availableBalance - order.stake
        return None

    def respond(self, time, markets, trade):
        return None


# --- AGENTS OF THE BETTING POOL BELOW --- #
# on initialisation will be given an exchange to operate on


class Agent_Random(BettingAgent):

    def getorder(self, time, markets):
        #if self.numOfBets > 0: return None
        r = random.randint(0,1)
        if(r == 0):
            c = random.randint(0, NUM_OF_COMPETITORS-1)
            e = random.randint(0, NUM_OF_EXCHANGES-1)
            minodds = 2
            maxodds = 8
            b = random.randint(0,1)
            if(b == 0):
                quoteodds = random.randint(minodds, minodds + 3)
                order = Order(e, self.id, c, 'Back', quoteodds, 1, markets[e][c]['QID'], time)
                #print("BACK MADE BY AGENT " + str(self.id))
            else:
                quoteodds = random.randint(maxodds - 6, maxodds)
                order = Order(e, self.id, c, 'Lay', quoteodds, 1, markets[e][c]['QID'], time)
                #print("LAY MADE BY AGENT " + str(self.id))
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


class Agent_Leader_Wins(BettingAgent):
    # This betting agent's view of the race outcome is that whichever competitor
    # that is currently in the lead after random number of timesteps between 5, 15
    # will win and will bet one better
    def __init__(self, id, name):
        BettingAgent.__init__(self, id, name)
        self.bettingTime = random.randint(5, 15)

    def getorder(self, time, markets):
        order = None
        if self.numOfBets >= 1 or self.raceStarted == False: return order
        if self.bettingTime <= self.raceTimestep:
            sortedComps = dict(sorted(self.currentRaceState.items(), key = lambda item: item[1]))
            compInTheLead = int(sortedComps[0][0])
            if markets[self.exchange][compInTheLead]['backs']['n'] > 0:
                quoteodds = markets[self.exchange][compInTheLead]['backs']['best'] + 1
            else:
                quoteodds = markets[self.exchange][compInTheLead]['backs']['worst']
            order = Order(self.exchange, self.id, compInTheLead, 'Back', quoteodds, markets[self.exchange][compInTheLead]['QID'], 1, time)
        return order
