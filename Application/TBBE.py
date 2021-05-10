### ~ THREADED BRISTOL BETTING EXCHANGE ~ ###

import sys, math, threading, time, queue, random, csv, config
from copy import deepcopy
from system_constants import *
from betting_agents import *
from race_simulator import Simulator
from ex_ante_odds_generator import *
from exchange import Exchange
from message_protocols import *
from session_stats import *

class Session:

    def __init__(self):
        # Initialise exchanges
        self.exchanges = {}
        self.exchangeOrderQs = {}
        self.exchangeThreads = []

        # Initialise betting agents
        self.bettingAgents = {}
        self.bettingAgentQs = {}
        self.bettingAgentThreads = []

        # Needed attributes
        self.startTime = None
        self.numberOfTimesteps = None
        self.lengthOfRace = None
        self.event = threading.Event()
        self.endOfInPlayBettingPeriod = None
        self.winningCompetitor = None

        self.generateRaceData()
        self.initialiseThreads()


    def exchangeLogic(self, exchange, exchangeOrderQ):
        """
        Logic for thread running the exchange
        """
        print("EXCHANGE " + str(exchange.id) + " INITIALISED...")

        self.event.wait()
        # While event is running, run logic for exchange
        while self.event.isSet():
            timeInEvent = (time.time() - self.startTime) / SESSION_SPEED_MULTIPLIER

            try: order = exchangeOrderQ.get(block=False)
            except: continue

            (transactions, markets) = exchange.processOrder(timeInEvent, order)

            if transactions != None:
                for id, q in self.bettingAgentQs.items():
                    update = exchangeUpdate(transactions, order, markets)
                    q.put(update)

        print("CLOSING EXCHANGE " + str(exchange.id))
        return 0


    def agentLogic(self, agent, agentQ):
        """
        Logic for betting agent threads
        """
        print("AGENT " + str(agent.id) + " INITIALISED...")
        # Need to have pre-event betting period
        self.event.wait()
        # Whole event is running, run logic for betting agents
        while self.event.isSet():
            time.sleep(0.01)
            timeInEvent = (time.time() - self.startTime) / SESSION_SPEED_MULTIPLIER
            order = None
            trade = None

            while agentQ.empty() is False:
                qItem = agentQ.get(block = False)
                if qItem.protocolNum == EXCHANGE_UPDATE_MSG_NUM:
                    for transaction in qItem.transactions:
                        if transaction['backer'] == agent.id: agent.bookkeep(transaction, 'Backer', qItem.order, timeInEvent)
                        if transaction['layer'] == agent.id: agent.bookkeep(transaction, 'Layer', qItem.order, timeInEvent)
                elif qItem.protocolNum == RACE_UPDATE_MSG_NUM:
                    agent.observeRaceState(qItem.timestep, qItem.compDistances)
                else:
                    print("INVALID MESSAGE")

            marketUpdates = {}
            for i in range(NUM_OF_EXCHANGES):
                marketUpdates[i] = self.exchanges[i].publishMarketState(timeInEvent)

            agent.respond(timeInEvent, marketUpdates, trade)
            order = agent.getorder(timeInEvent, marketUpdates)
            #print("ORDER: " + str(order))

            if order != None:
                if TBBE_VERBOSE: print(order)
                agent.numOfBets = agent.numOfBets + 1
                self.exchangeOrderQs[order.exchange].put(order)

        print("ENDING AGENT " + str(agent.id))
        return 0

    def populateMarket(self):
        """
        Populate market with betting agents as specified in config file
        """
        def initAgent(name, quantity, id):
            if name == 'Test': return Agent_Test(id, name, self.lengthOfRace, self.endOfInPlayBettingPeriod)
            if name == 'Random': return Agent_Random(id, name, self.lengthOfRace, self.endOfInPlayBettingPeriod)
            if name == 'Leader_Wins': return Agent_Leader_Wins(id, name, self.lengthOfRace, self.endOfInPlayBettingPeriod)
            if name == 'Underdog': return Agent_Underdog(id, name, self.lengthOfRace, self.endOfInPlayBettingPeriod)
            if name == 'Back_Favourite': return Agent_Back_Favourite(id, name, self.lengthOfRace, self.endOfInPlayBettingPeriod)
            if name == 'Linex': return Agent_Linex(id, name, self.lengthOfRace, self.endOfInPlayBettingPeriod)
            if name == 'Arbitrage': return Agent_Arbitrage(id, name, self.lengthOfRace, self.endOfInPlayBettingPeriod)
            if name == 'Priveledged': return Agent_Priveledged(id, name, self.lengthOfRace, self.endOfInPlayBettingPeriod)

        id = 0
        for agent in config.agents:
            type = agent[0]
            for i in range(agent[1]):
                self.bettingAgents[id] = initAgent(agent[0], agent[1], id)
                id = id + 1

    def initialiseExchanges(self):
        """
        Initialise exchanges, returns list of exchange objects
        """
        for i in range(NUM_OF_EXCHANGES):
            self.exchanges[i] = Exchange(i, NUM_OF_COMPETITORS) # NUM_OF_COMPETITORS may be changed to list of competitor objects that are participating
            self.exchangeOrderQs[i] = queue.Queue()

    def initialiseBettingAgents(self):
        """
        Initialise betting agents
        """
        self.populateMarket()
        # Create threads for all betting agents that wait until event session
        # has started
        for id, agent in self.bettingAgents.items():
            self.bettingAgentQs[id] = queue.Queue()
            thread = threading.Thread(target = self.agentLogic, args = [agent, self.bettingAgentQs[id]])
            self.bettingAgentThreads.append(thread)

    def updateRaceQ(self, timestep):
        """
        Read in race data and update agent queues with competitor distances at timestep
        """
        with open(RACE_DATA_FILENAME, 'r') as file:
            reader = csv.reader(file)
            r = [row for index, row in enumerate(reader) if index == timestep]
        time = r[0][0]
        compDistances = {}
        for c in range(NUM_OF_COMPETITORS):
            compDistances[c] = float(r[0][c+1])

        # Create update
        update = raceUpdate(time, compDistances)

        for id, q in self.bettingAgentQs.items():
            q.put(update)

    def preRaceBetPeriod(self):
        print("Start of pre-race betting period, lasting " + str(PRE_RACE_BETTING_PERIOD_LENGTH))
        time.sleep(PRE_RACE_BETTING_PERIOD_LENGTH / SESSION_SPEED_MULTIPLIER)
        print("End of pre-race betting period")
        # marketUpdates = {}
        # for id, ex in exchanges.items():
        #     timeInEvent = time.time() - startTime
        #     print("Exchange " + str(id) + " markets: ")
        #     print(exchanges[id].publishMarketState(timeInEvent))


    def eventSession(self, simulationId):
        """
        Set up and management of race event
        """

        # Record start time
        self.startTime = time.time()

        # Start exchange threads
        for id, exchange in self.exchanges.items():
            thread = threading.Thread(target = self.exchangeLogic, args = [exchange, self.exchangeOrderQs[id]])
            self.exchangeThreads.append(thread)

        for thread in self.exchangeThreads:
            thread.start()

        # Start betting agent threads
        for thread in self.bettingAgentThreads:
            thread.start()

        # Initialise event
        self.event.set()

        time.sleep(0.01)

        # Pre-race betting period
        self.preRaceBetPeriod()


        # have loop which runs until competitor has won race
        i = 0
        while(i < self.numberOfTimesteps):
            self.updateRaceQ(i+1)
            i = i+1
            if TBBE_VERBOSE: print(i)
            print(i)
            # run simulation
            #race.updateRaceState()
            #race.saveRaceState(0)

            # call update function of every betting agent
            #updateAgents(competitors, agents)

            # for i in range(len(race.competitors)):
            #     #print(str(race.competitors[i]) + " : " +
            #          #str(race.competitors[i].distance))
            #     if(race.competitors[i].distance >= race.race_attributes.length):
            #        winner = race.competitors[i].id
            #        print("WINNER: " + str(winner))

            time.sleep(1 / SESSION_SPEED_MULTIPLIER)


        # End event
        self.event.clear()

        # Close threads
        for thread in self.exchangeThreads: thread.join()
        for thread in self.bettingAgentThreads: thread.join()

        print("Simulation complete")

        print("Writing data....")
        for id, ex in self.exchanges.items():
            for orderbook in ex.compOrderbooks:
                for trade in orderbook.tape:
                    print(trade)

        # Settle up all transactions over all exchanges
        for id, ex in self.exchanges.items():
            ex.settleUp(self.bettingAgents, self.winningCompetitor)

        # for id, exchange in exchanges.items():
        #     exchange.tapeDump('transactions.csv', 'a', 'keep')

        for id, agent in self.bettingAgents.items():
            print("Agent " + str(id) + "\'s final balance: " + str(agent.balance))

        createstats(self.bettingAgents)

    def initialiseThreads(self):
        self.initialiseExchanges()
        self.initialiseBettingAgents()

    def generateRaceData(self):
        # Create race event data
        race = Simulator(NUM_OF_COMPETITORS)
        compPool = deepcopy(race.competitors)
        raceAttributes = deepcopy(race.race_attributes)


        # create simulations for procurement of ex-ante odds for priveledged betters
        createExAnteOdds(compPool, raceAttributes)

        race.run("core")
        self.numberOfTimesteps = race.numberOfTimesteps
        self.lengthOfRace = race.race_attributes.length
        self.winningCompetitor = race.winner
        self.endOfInPlayBettingPeriod = race.winningTimestep - IN_PLAY_CUT_OFF_PERIOD

        createInPlayOdds(self.numberOfTimesteps)

    # MAIN LOOP
    def runSession(self):
        # Simulation attributes
        currentSimulation = 0
        ####################

        # set things up
        # have while loop for running multiple races
        # within loop instantiate competitors into list
        # run simulation and matching engine
        while currentSimulation < NUM_OF_SIMS:
            simulationId = "Simulation: " + str(currentSimulation)


            # Start up thread for race on which all other threads will wait
            self.eventSession(simulationId)

            currentSimulation = currentSimulation + 1






if __name__ == "__main__":
    sess = Session()
    sess.runSession()
