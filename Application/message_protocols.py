### ~ THREADED BRISTOL BETTING EXCHANGE ~ ###

# Message protocols for information transfer between Exchange and Betting Agents

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
        self.timestamp = time

    def __str__(self):
        return ("Order: [Agent ID: " + str(self.agentId) +
                " Betting on competitor: " + str(self.competitorId) +
                " Direction: " + str(self.direction) + " Odds: " +
                str(self.odds) + " Stake: " + str(self.stake) + " Order ID: " +
                str(self.orderId) + " Timestamp: " + self.timestamp + "]")
