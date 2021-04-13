### ~ THREADED BRISTOL BETTING EXCHANGE ~ ###

'''
Page 56 - The Perfect Bet
Strategy by Benter -> Find predicted odds then combine with markets as markets may contain privileged infomation

Should be stock pool of betting agents representing normal civilian bettors (eg. with range from less to more privileged info - recreational and insiders (eg. knowing diet / jockey strat))


'''



import sys, math, threading, time, queue, random, csv, config, random, operator
from message_protocols import Order
from system_constants import *
from ex_ante_odds_generator import getExAnteOdds, getInPlayOdds

class BettingAgent:
    def __init__(self, id, name, lengthOfRace, endOfInPlayBettingPeriod, exchange = None):
        self.id = id
        self.name = name
        self.balance = 500
        self.availableBalance = self.balance
        self.orders = []
        self.numOfBets = 0 # Number of bets live on BBE
        self.exchange = random.randint(0, NUM_OF_EXCHANGES-1)
        self.endOfInPlayBettingPeriod = endOfInPlayBettingPeriod
        self.bettingPeriod = True

        # race details
        self.lengthOfRace = lengthOfRace
        self.raceStarted = False
        self.raceTimestep = 0
        self.currentRaceState = {}
        self.raceHistoryDists = {}

    def observeRaceState(self, timestep, compDistances):
        if self.raceStarted == False: self.raceStarted = True
        for id, dist in compDistances.items():
            self.currentRaceState[id] = dist
            if id not in self.raceHistoryDists:
                self.raceHistoryDists[id] = []
            self.raceHistoryDists[id].append(dist)
        self.raceTimestep = int(timestep)
        if int(timestep) >= self.endOfInPlayBettingPeriod:
            self.bettingPeriod = False


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
        if self.bettingPeriod == False: return None
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

#
# class Agent_Random(BettingAgent):
#     def __init__(self, id, name, lengthOfRace):
#         BettingAgent.__init__(id, name, lengthOfRace)
#
#
#     def getorder(self, time, markets):
#         #if self.numOfBets > 0: return None
#         r = random.randint(0,1)
#         if(r == 0):
#             c = random.randint(0, NUM_OF_COMPETITORS-1)
#             e = random.randint(0, NUM_OF_EXCHANGES-1)
#             minodds = 2
#             maxodds = 8
#             b = random.randint(0,1)
#             if(b == 0):
#                 quoteodds = random.randint(minodds, minodds + 3)
#                 order = Order(e, self.id, c, 'Back', quoteodds, 1, markets[e][c]['QID'], time)
#                 #print("BACK MADE BY AGENT " + str(self.id))
#             else:
#                 quoteodds = random.randint(maxodds - 6, maxodds)
#                 order = Order(e, self.id, c, 'Lay', quoteodds, 1, markets[e][c]['QID'], time)
#                 #print("LAY MADE BY AGENT " + str(self.id))
#         else:
#             order = None
#
#         return order
#
#     def respond(self, time, markets, trade):
#





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
    def __init__(self, id, name, lengthOfRace, endOfInPlayBettingPeriod):
        BettingAgent.__init__(self, id, name, lengthOfRace, endOfInPlayBettingPeriod)
        self.bettingTime = random.randint(5, 15)

    def getorder(self, time, markets):
        if self.bettingPeriod == False: return None
        order = None
        if self.numOfBets >= 1 or self.raceStarted == False: return order
        if self.bettingTime <= self.raceTimestep:
            sortedComps = sorted((self.currentRaceState.items()), key = operator.itemgetter(1))
            compInTheLead = int(sortedComps[len(sortedComps)-1][0])
            if markets[self.exchange][compInTheLead]['backs']['n'] > 0:
                quoteodds = max(MIN_ODDS, markets[self.exchange][compInTheLead]['backs']['best'] - 1)
            else:
                quoteodds = markets[self.exchange][compInTheLead]['backs']['worst']
            order = Order(self.exchange, self.id, compInTheLead, 'Back', quoteodds, 1, markets[self.exchange][compInTheLead]['QID'], time)
        return order

class Agent_Underdog(BettingAgent):
    # This betting agent's view of the race outcome is that the competitor in
    # second place will win if distance between it and the winner is small
    # if competitor in second place falls too far behind then agent will lay the
    # second place competitor and back the winning competitor
    def __init__(self, id, name, lengthOfRace, endOfInPlayBettingPeriod):
        BettingAgent.__init__(self, id, name, lengthOfRace, endOfInPlayBettingPeriod)
        self.bettingTime = random.randint(5, 15)
        self.threshold = random.randint(10, 35)
        self.compInTheLead = None
        self.compInSecond = None
        self.job = None

    def observeRaceState(self, timestep, compDistances):
        super().observeRaceState(timestep, compDistances)
        if self.bettingTime <= self.raceTimestep:
            sortedComps = sorted(self.currentRaceState.items(), key = operator.itemgetter(1))
            #print(sortedComps)
            #print(sortedComps[0][0])
            compInTheLead = sortedComps[len(sortedComps)-1]
            compInSecond = sortedComps[len(sortedComps)-2]

            if float(compInTheLead[1]) <= (float(compInSecond[1]) + float(self.threshold)) and compInTheLead[0] != self.compInTheLead:
                self.job = "back_underdog"
                self.compInTheLead = compInTheLead[0]
                self.compInSecond = compInSecond[0]

    def getorder(self, time, markets):
        order = None
        if self.numOfBets >= 10 or self.raceStarted == False or self.bettingPeriod == False: return order
        if self.bettingTime <= self.raceTimestep:
            if self.job == 'back_underdog':
                if markets[self.exchange][self.compInSecond]['backs']['n'] > 0:
                    quoteodds = max(MIN_ODDS, markets[self.exchange][self.compInSecond]['backs']['best'] - 1)
                else:
                    quoteodds = markets[self.exchange][self.compInTheLead]['backs']['worst']
                order = Order(self.exchange, self.id, self.compInSecond, 'Back', quoteodds, 1, markets[self.exchange][self.compInSecond]['QID'], time)
                self.job = "lay_leader"

            elif self.job == 'lay_leader':
                if markets[self.exchange][self.compInTheLead]['lays']['n'] > 0:
                    quoteodds = markets[self.exchange][self.compInTheLead]['lays']['best'] + 1
                else:
                    quoteodds = markets[self.exchange][self.compInTheLead]['lays']['worst']
                order = Order(self.exchange, self.id, self.compInTheLead, 'Lay', quoteodds, 1, markets[self.exchange][self.compInTheLead]['QID'], time)
                self.job = None
        return order


class Agent_Back_Favourite(BettingAgent):
    # This betting agent will place a back bet on the markets favourite to win (lowest back odds),
    # hence not having any priveledged view on which competitor will win the race
    # but instead relies on that information being ingrained in the market state
    def __init__(self, id, name, lengthOfRace, endOfInPlayBettingPeriod):
        BettingAgent.__init__(self, id, name, lengthOfRace, endOfInPlayBettingPeriod)
        self.marketsFave = None

    def getorder(self, time, markets):
        if self.bettingPeriod == False: return None
        order = None
        marketsFave = None
        lowestOdds = MAX_ODDS
        for comp in markets[self.exchange]:
            market = markets[self.exchange][comp]
            if market['backs']['n'] > 0:
                bestodds = market['backs']['best']
                if bestodds < lowestOdds:
                    lowestOdds = bestodds
                    marketsFave = comp
        #print("MARKET FAVE IS: " + str(marketsFave))


        if marketsFave == self.marketsFave:
            # market favourite hasn't changed therefore no need to back again
            return None

        elif marketsFave != None:
            self.marketsFave = marketsFave
            quoteodds = max(MIN_ODDS, lowestOdds - 0.1)
            order = Order(self.exchange, self.id, marketsFave, 'Back', quoteodds, 1, markets[self.exchange][marketsFave]['QID'], time)

        return order

class Agent_Linex(BettingAgent):
    # This betting agent's view of the race result stems from performing linear
    # extrapolation for each competitor to see which will finish first, calculated
    # winner is then backed whilst the worst competitor is layed, only starts
    # recording after random amount of time so as to avoid interference at start of race
    def __init__(self, id, name, lengthOfRace, endOfInPlayBettingPeriod):
        BettingAgent.__init__(self, id, name, lengthOfRace, endOfInPlayBettingPeriod)
        self.timeSinceLastBet = 0
        self.bettingInterval = random.randint(30, 60)
        self.recordingTime = random.randint(5, 15)
        self.n = random.randint(15, 25)
        self.predictedResults = {}
        self.predictedWinner = None
        self.predictedLoser = None
        self.injuredCompetitors= []
        self.job = None
        self.predicted = False

    def predict(self):
        predictedWinnerTime = 10000
        predictedLoserTime = 0
        for i in range(NUM_OF_COMPETITORS):
            if i in self.injuredCompetitors: continue
            dists = self.raceHistoryDists[i]
            fromDist = float(dists[len(dists) - self.n])
            toDist = float(dists[-1])
            timeTaken = float(len(dists))
            avgSpeed = (toDist - fromDist) / timeTaken
            distLeft = self.lengthOfRace - toDist

            try:
                self.predictedResults[i] = distLeft / avgSpeed
            except:
                # competitor has been injured / cannot race further
                self.injuredCompetitors.append(i)
                continue
            if self.predictedWinner == None or self.predictedResults[i] < predictedWinnerTime:
                self.predictedWinner = i
                predictedWinnerTime = self.predictedResults[i]
            elif self.predictedLoser == None or self.predictedResults[i] > predictedLoserTime:
                self.predictedLoser = i
                predictedLoserTime = self.predictedResults[i]


        self.predicted = True

    def observeRaceState(self, timestep, compDistances):
        super().observeRaceState(timestep, compDistances)
        if self.bettingPeriod == False: return

        if len(self.raceHistoryDists[0]) > (self.n + self.recordingTime) and self.predicted == False:
            self.predict()
            if self.predictedWinner != None:
                self.job = "back_pred_winner"

        if self.predicted == True:
            self.timeSinceLastBet = self.timeSinceLastBet + 1
            if self.timeSinceLastBet >= self.bettingInterval:
                self.predicted = False
                self.timeSinceLastBet = 0

    def getorder(self, time, markets):
        order = None
        if self.predicted == False or self.bettingPeriod == False: return order

        #print(self.predictedWinner)
        #print("LOSER: " + str(self.predictedLoser))

        if self.job == 'back_pred_winner':
            if markets[self.exchange][self.predictedWinner]['backs']['n'] > 0:
                quoteodds = max(MIN_ODDS, markets[self.exchange][self.predictedWinner]['backs']['best'] - 0.1)
            else:
                quoteodds = markets[self.exchange][self.predictedWinner]['backs']['worst']
                print("WORST ODDS: " + str(quoteodds))
            order = Order(self.exchange, self.id, self.predictedWinner, 'Back', quoteodds, 1, markets[self.exchange][self.predictedWinner]['QID'], time)
            self.job = "lay_pred_loser"

        elif self.job == 'lay_pred_loser':
            print("LAYING: " +str(self.predictedLoser))
            if markets[self.exchange][self.predictedLoser]['lays']['n'] > 0:
                quoteodds = markets[self.exchange][self.predictedLoser]['lays']['best'] + 0.1
            else:
                quoteodds = markets[self.exchange][self.predictedLoser]['lays']['worst']
            order = Order(self.exchange, self.id, self.predictedLoser, 'Lay', quoteodds, 1, markets[self.exchange][self.predictedLoser]['QID'], time)
            self.job = None

        return order

class Agent_Priveledged(BettingAgent):
    '''
    create reasonable ex ante odds for rest of bettors (no random till in play and then use best back/lay)
    when in play will be able to run one simulation every 10/15 time steps
    this will simulate snap decisions within in-play betting
    greater inefficiencies in in play betting markets because more data point all of which
    have Uncertainty
    '''
    def __init__(self, id, name, lengthOfRace, endOfInPlayBettingPeriod):
        BettingAgent.__init__(self, id, name, lengthOfRace, endOfInPlayBettingPeriod)
        self.exAnteOdds = getExAnteOdds(self.id)


        print("AGENT ID: " + str(self.id) + " " + str(self.id) + " Ex Ante Odds Pred: " + str(self.exAnteOdds))

    def getExAnteOrder(self, time, markets):
        for i in range(len(self.exAnteOdds)):
            odds = self.exAnteOdds[i]
            direction = 'Back'
            if int(odds) == 0:
                direction = 'Lay'
                odds = MAX_ODDS

            order = Order(self.exchange, self.id, i, direction, odds, 1, markets[self.exchange][i]['QID'], time)
            self.orders.append(order)
            #print("AGENT " + str(self.id) + ": " + str(order))

    def getInPlayOrder(self, time, markets):
        odds = getInPlayOdds(self.id, self.currentRaceState)
        #print(odds)
        return

    def getorder(self, time, markets):
        order = None
        if self.bettingPeriod == False: return order
        if self.raceStarted == False:
            self.getExAnteOrder(time, markets)
        else:
            self.getInPlayOrder(time, markets)

        if len(self.orders) > 0:
            order = self.orders.pop(0)

        return order
