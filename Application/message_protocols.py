### ~ THREADED BRISTOL BETTING EXCHANGE ~ ###

# Message protocols for information transfer between Exchange and Betting Agents

from system_constants import *

class Order:
    """
    Protocol for issuing a new order, from betting agent to exchange
    """
    def __init__(self, exchange, agentId, competitorId, direction, odds, stake, orderId, timestamp):
        self.exchange = exchange
        self.agentId = agentId
        self.competitorId = competitorId
        self.direction = direction
        self.odds = odds
        self.stake = stake
        self.orderId = orderId
        self.timestamp = timestamp

    def __str__(self):
        return ("Order: [Agent ID: " + str(self.agentId) +
                " Betting on competitor: " + str(self.competitorId) +
                " Direction: " + str(self.direction) + " Odds: " +
                str(self.odds) + " Stake: " + str(self.stake) + " Order ID: " +
                str(self.orderId) + " Timestamp: " + str(self.timestamp) + "]")

class exchangeUpdate:
    """
    Protocol for transfer of trade information between exchange and betting agents
    """
    def __init__(self, transactions, order, markets):
        self.protocolNum = EXCHANGE_UPDATE_MSG_NUM
        self.transactions = transactions
        self.order = order
        self.markets = markets

class raceUpdate:
    """
    Protocol for transfer of new race information to betting agents
    """
    def __init__(self, timestep, competitorDistances):
        self.protocolNum = RACE_UPDATE_MSG_NUM
        self.timestep = timestep
        self.compDistances = competitorDistances
