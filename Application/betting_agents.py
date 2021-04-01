### ~ THREADED BRISTOL BETTING EXCHANGE ~ ###

import sys, math, threading, time, queue, random, csv, config
from message_protocols import Order

class BettingAgent:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.balance = 500
        self.orders = {}
        self.numOfBets = 0 # Number of bets live on BBE

    def bookkeep(self, trade, order, time):
        self.numOfBets = self.numOfBets - 1
        return None

    def respond(self, time, markets, trade):
        return None

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
