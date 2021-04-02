### ~ THREADED BRISTOL BETTING EXCHANGE ~ ###

import sys, config
from system_constants import EXCHANGE_VERBOSE, MIN_ODDS, MAX_ODDS, NUM_OF_COMPETITORS
from betting_agents import *
from race_simulator import Simulator
from message_protocols import Order

# Orderbook_half is one side of the book: a list of bids or a list of lays, each sorted best-first
class OrderbookHalf:
	def __init__(self, booktype, worstodds):
		# booktype: backs or lays?
		self.booktype = booktype
		# dictionary of orders received, indexed by Betting Agent ID
		self.orders = {}
		# the market, dictionary indexed by price, with order info
		self.market = {}
		# anonymized market, list of two-valued lists, only odds/stake info
		self.anonymisedMarket = []
		# summary stats
		self.bestOdds = None
		self.bestAgentId = None
		self.worstOdds = worstodds
		self.numOfOrders = 0  # how many orders?
		self.marketDepth = 0  # how many different prices in market?


	def anonymiseMarket(self):
		"""
		Anonymise market and format as a sorted list [[odds, stake]]
		"""
		# anonymise the market, strip out order details, format as a sorted list
		# NB for lays, the sorting should be reversed
		self.anonymisedMarket = []
		for odds in list(sorted(self.market)):
			stake = self.market[odds][0]
			self.anonymisedMarket.append([odds, stake])


	def buildMarket(self):
		"""
		Build market from list of orders, returns an unsorted dictionary [odds, [order info]]
		"""
		# take a list of orders and build the betting market from it
		# NB the exchange needs to know arrival times and betting agent id associated with each order
		# returns as a dictionary (i.e., unsorted)
		# also builds anonymized version (just price/quantity, sorted, as a list) for publishing to betting agents
		self.market = {}

		for key, order in self.orders.items():
			odds = order.odds
			if odds in self.market:
				# update existing entry
				stake = self.market[odds][0]
				orderList = self.market[odds][1]
				orderList.append([order.timestamp, order.stake, order.agentId, order.orderId])
				self.market[odds] = [stake + order.stake, orderList]
			else:
				# create a new dictionary entry
				self.market[odds] = [order.stake, [[order.timestamp, order.stake, order.agentId, order.orderId]]]
		# create anonymized version
		self.anonymiseMarket()
		# record best price and associated betting agent id
		if len(self.market) > 0 :
			if self.booktype == 'Back':
				self.bestOdds = self.anonymisedMarket[-1][0]
			else :
				self.bestOdds = self.anonymisedMarket[0][0]
			self.bestAgentId = self.market[self.bestOdds][1][0][2]
		else :
			self.bestOdds = None
			self.bestAgentId = None

		if EXCHANGE_VERBOSE : print(self.market)


	def bookAddOrder(self, order):
		"""
		Should order be added or should existing order be overwritten,
		returns as string instruction
		"""
		# add order to the dictionary holding the list of orders
		# either overwrites old order from this betting agent
		# or dynamically creates new entry in the dictionary
		# so, max of one order per trader per list
		# checks whether length or order list has changed, to distinguish addition/overwrite

		numOfOrdersBefore = self.numOfOrders
		self.orders[order.agentId] = order
		self.numOfOrders = len(self.orders)
		self.buildMarket()

		if numOfOrdersBefore != self.numOfOrders :
			return('Addition')
		else:
			return('Overwrite')



	def bookDeleteOrder(self, order):
		"""
		Delete order from orders dictionary, assuming one order per trader
		"""
		# delete order from the dictionary holding the orders
		# assumes max of one order per trader per list
		# checks that the Trader ID does actually exist in the dict before deletion

		if self.orders.get(order.agentId) != None :
			del(self.orders[order.agentId])
			self.numOfOrders = len(self.orders)
			self.buildMarket()


	def bookDeleteBest(self):
		"""
		Delete order from book when has been fulfilled, returns agent ID of
		order as the counterparty
		"""
		# delete order: when the best bid/ask has been hit, delete it from the book
		# the betting agent id of the deleted order is return-value, as counterparty to the trade
		bestOddsOrders = self.market[self.bestOdds]
		bestOddsStake = bestOddsOrders[0]
		bestOddsCounterparty = bestOddsOrders[1][0][2]
		if bestOddsStake == 1:
			# here the order deletes the best odds
			del(self.market[self.bestOdds])
			del(self.orders[bestOddsCounterparty])
			self.numOfOrders = self.numOfOrders - 1
			if self.numOfOrders > 0:
				if self.booktype == 'Back':
					self.bestOdds = max(self.market.keys())
				else:
					self.bestOdds = min(self.market.keys())
				self.marketDepth = len(self.market.keys())
			else:
				self.bestOdds = self.worstOdds
				self.marketDepth = 0
		else:
			# stake > 1 so the order decrements the quantity of the best back
			# update the market with the decremented order data
			self.market[self.bestOdds] = [bestOddsStake - 1, bestOddsOrders[1][1:]]

			# update the back list: counterparty's back has been deleted
			del(self.orders[bestOddsCounterparty])
			self.numOfOrders = self.numOfOrders - 1
		self.buildMarket()
		return bestOddsCounterparty



# Orderbook for a single instrument: list of backs and list of lays

class Orderbook(OrderbookHalf):

	def __init__(self, competitorId):
		self.competitorId = competitorId
		self.backs = OrderbookHalf('Back', MIN_ODDS)
		self.lays = OrderbookHalf('Lay', MAX_ODDS)
		self.tape = []
		self.quoteId = 0  #unique ID code for each quote accepted onto the book


# Exchange's internal orderbook

class Exchange(Orderbook):
	# Need to take in number of competitors and create an individual orderbook for each
	def __init__(self, id, numOfCompetitors):
		self.id = id
		# list of unique orderbooks for all competitors
		self.compOrderbooks = []
		for i in range(numOfCompetitors):
			self.compOrderbooks.append(Orderbook(i))


	def addOrder(self, order):
		"""
		Add order to exchange, updating all internal records, returns order ID
		"""
		# add a quote/order to the exchange and update all internal records; return unique i.d.
		# retrieve orderbook for competitor in question
		orderbook = self.compOrderbooks[order.competitorId]

		order.orderId = orderbook.quoteId
		orderbook.quoteId = order.orderId + 1

		if order.direction == 'Back':
			response = orderbook.backs.bookAddOrder(order)
			bestOdds = orderbook.backs.anonymisedMarket[-1][0]
			orderbook.backs.bestOdds = bestOdds
			orderbook.backs.bestAgentId = orderbook.backs.market[bestOdds][1][0][2]
		else:
			response = orderbook.lays.bookAddOrder(order)
			bestOdds = orderbook.lays.anonymisedMarket[0][0]
			orderbook.lays.bestOdds = bestOdds
			orderbook.lays.bestAgentId = orderbook.lays.market[bestOdds][1][0][2]
		return [order.orderId, response]


	def delOrder(self, time, order):
		"""
		Delete order from exchange, update all internal records, returns order ID
		"""
		# delete a betting agent's order from the exchange, update all internal records

		# retrieve orderbook for competitor in question
		orderbook = self.compOrderbooks[order.competitorId]

		if order.direction == 'Back':
			orderbook.backs.bookDeleteOrder(order)
			if orderbook.backs.numOfOrders > 0 :
				bestOdds = orderbook.backs.anonymisedMarket[-1][0]
				orderbook.backs.bestOdds = bestOdds
				orderbook.backs.bestAgentId = orderbook.backs.market[bestOdds][1][0][2]
			else: # this side of book is empty
				orderbook.backs.bestOdds = None
				orderbook.backs.bestAgentId = None
			cancelRecord = { 'type': 'Cancel', 'time': time, 'order': order }
			orderbook.tape.append(cancelRecord)

		elif order.direction == 'Lay':
			orderbook.lays.bookDeleteOrder(order)
			if orderbook.lays.numOfOrders > 0 :
				bestOdds = orderbook.lays.anonymisedMarket[0][0]
				orderbook.lays.bestOdds = bestOdds
				orderbook.lays.bestAgentId = orderbook.lays.market[bestOdds][1][0][2]
			else: # this side of book is empty
				orderbook.lays.bestOdds = None
				orderbook.lays.bestAgentId = None
			cancelRecord = { 'type': 'Cancel', 'time': time, 'order': order }
			orderbook.tape.append(cancelRecord)
		else:
			# neither back nor lay?
			sys.exit('bad order type in delOrder')

	# this returns the LOB data "published" by the exchange,
	# i.e., what is accessible to the betting agents
	def publishMarketState(self, time):
		"""
		Publish market state to betting agents, returns dictionary of best,
		worst, number and anonymised market state
		"""
		competitorsMarkets = {}
		for book in self.compOrderbooks:
			publicData = {}
			publicData['time'] = time
			publicData['backs'] = {'best':book.backs.bestOdds,
									'worst':book.backs.worstOdds,
									'n': book.backs.numOfOrders,
									'market':book.backs.anonymisedMarket}
			publicData['lays'] = {'best':book.lays.bestOdds,
									'worst':book.lays.worstOdds,
									'n': book.lays.numOfOrders,
									'market':book.lays.anonymisedMarket}
			publicData['QID'] = book.quoteId
			publicData['tape'] = book.tape
			competitorsMarkets[book.competitorId] = publicData

			# if EXCHANGE_VERBOSE:
			# 	print("Market Published at timestamp: " + str(time) + " - BACKS[" +
			# 	str(publicData['backs']['market']) + "] LAYS[" +
			# 	str(publicData['lays']['market']) + "]")

		return competitorsMarkets



	def processOrder(self, time, order):
		"""
		Process order by either adding to back or lay market (limit order) or
		if crosses best counterparty offer then execute (market order), returns
		record of transaction and new market state (publishMarketState)
		"""
		# receive an order and either add it to the relevant market (treat as limit order)
		# or if it crosses the best counterparty offer, execute it (treat as a market order)

		# retrieve orderbook for competitor in question
		orderbook = self.compOrderbooks[order.competitorId]

		orderOdds = order.odds
		counterparty = None
		#counter_coid = None
		[orderId, response] = self.addOrder(order)  # add it to the order lists -- overwriting any previous order
		order.orderId = orderId
		if EXCHANGE_VERBOSE :
			print("Order ID: " + str(order.orderId))
			print("Reponse is: " + response)
		bestLay = orderbook.lays.bestOdds
		bestLayAgentId = orderbook.lays.bestAgentId
		bestBack = orderbook.backs.bestOdds
		bestBackAgentId = orderbook.backs.bestAgentId
		if order.direction == 'Back':
			if orderbook.lays.numOfOrders > 0 and bestBack >= bestLay:
				# bid lifts the best ask
				if EXCHANGE_VERBOSE: print("Back $%s lifts best lay" % orderOdds)
				counterparty = bestLayAgentId
				#counter_coid = self.lays.orders[counterparty].coid
				odds = bestLay  # bid crossed ask, so use ask price
				# delete the ask just crossed
				orderbook.lays.bookDeleteBest()
				# delete the bid that was the latest order
				orderbook.backs.bookDeleteBest()
		elif order.direction == 'Lay':
			if orderbook.backs.numOfOrders > 0 and bestLay <= bestBack:
				# ask hits the best bid
				if EXCHANGE_VERBOSE: print("Lay $%s hits best back" % orderOdds)
				# remove the best bid
				counterparty = bestBackAgentId
				#counter_coid = self.bids.orders[counterparty].coid
				odds = bestBack  # ask crossed bid, so use bid price
				# delete the bid just crossed, from the exchange's records
				orderbook.backs.bookDeleteBest()
				# delete the ask that was the latest order, from the exchange's records
				orderbook.lays.bookDeleteBest()
		else:
			# we should never get here
			sys.exit('processOrder given neither Back nor Lay')
		# NB at this point we have deleted the order from the exchange's records
		# but the two traders concerned still have to be notified
		if EXCHANGE_VERBOSE: print("Counterparty: " + str(counterparty))

		markets = self.publishMarketState(time)
		if counterparty != None:
			# process the trade
			if EXCHANGE_VERBOSE:
				print(">>>>>>>>> TRADE at TIME:" + str(time) + ", ODDS of: " +
				str(odds) + " as a: " + str(order.direction) + " FROM: " +
				str(order.agentId) + ", WITH: " + str(counterparty))

			if order.direction == 'Back':
				backer = order.agentId
				layer = counterparty
			else:
				backer = counterparty
				layer = order.agentId

			transactionRecord = { 'type': 'Trade',
									'time': time,
									'exchange': order.exchange,
									'competitor': order.competitorId,
									'odds': odds,
									'backer':backer,
									'layer':layer,
									'stake': order.stake
									}
			orderbook.tape.append(transactionRecord)

			return (transactionRecord, markets)

		else:
			return (None, markets)



	def tapeDump(self, fname, fmode, tmode):
		dumpfile = open(fname, fmode)
		for id in range(NUM_OF_COMPETITORS):
			orderbook = self.compOrderbooks[id]
			for tapeitem in orderbook.tape:
				if tapeitem['type'] == 'Trade' :
					dumpfile.write('%s, %s\n' % (tapeitem['time'], tapeitem['odds']))
			dumpfile.close()
			if tmode == 'wipe':
				orderbook.tape = []
