### ~ THREADED BRISTOL BETTING EXCHANGE ~ ###

import sys, math, threading, time, queue, random, csv, config
from system_constants import *
from betting_agents import *
from race_simulator import Simulator
from exchange import Exchange
from message_protocols import *

def exchangeLogic(exchange, exchangeOrderQ, bettingAgentQs, event, startTime, numberOfTimesteps):
    """
    Logic for thread running the exchange
    """
    print("EXCHANGE " + str(exchange.id) + " INITIALISED...")

    event.wait()
    # While event is running, run logic for exchange
    while event.isSet():
        timeInEvent = (time.time() - startTime) * numberOfTimesteps

        try: order = exchangeOrderQ.get(block=False)
        except: continue

        (trade, markets) = exchange.processOrder(timeInEvent, order)

        if trade != None:
            for id, q in bettingAgentQs.items():
                update = exchangeUpdate(trade, order, markets)
                q.put(update)

    print("CLOSING EXCHANGE " + str(exchange.id))
    return 0


def agentLogic(agent, agentQ, exchanges, exchangeOrderQs, event, startTime, numberOfTimesteps):
    """
    Logic for betting agent threads
    """
    print("AGENT " + str(agent.id) + " INITIALISED...")
    # Need to have pre-event betting period
    event.wait()
    # Whole event is running, run logic for betting agents
    while event.isSet():
        time.sleep(0.01)
        timeInEvent = (time.time() - startTime) * numberOfTimesteps
        order = None
        trade = None

        while agentQ.empty() is False:
            qItem = agentQ.get(block = False)
            if qItem.protocolNum == EXCHANGE_UPDATE_MSG_NUM:
                if qItem.trade['backer'] == agent.id: agent.bookkeep(qItem.trade, qItem.order, timeInEvent)
                if qItem.trade['layer'] == agent.id: agent.bookkeep(qItem.trade, qItem.order, timeInEvent)
            elif qItem.protocolNum == RACE_UPDATE_MSG_NUM:
                agent.observeRaceState(qItem.timestep, qItem.compDistances)
            else:
                print("INVALID MESSAGE")

        marketUpdates = {}
        for i in range(NUM_OF_EXCHANGES):
            marketUpdates[i] = exchanges[i].publishMarketState(timeInEvent)

        agent.respond(timeInEvent, marketUpdates, trade)
        order = agent.getorder(timeInEvent, marketUpdates)
        #print("ORDER: " + str(order))

        if order != None:
            if TBBE_VERBOSE: print(order)
            agent.numOfBets = agent.numOfBets + 1
            exchangeOrderQs[order.exchange].put(order)

    print("ENDING AGENT " + str(agent.id))
    return 0

def populateMarket(bettingAgents):
    """
    Populate market with betting agents as specified in config file
    """
    def initAgent(name, quantity, id):
        if name == 'Test': return Agent_Test(id, name)

    id = 0
    for agent in config.agents:
        type = agent[0]
        for i in range(agent[1]):
            bettingAgents[id] = initAgent(agent[0], agent[1], id)
            id = id + 1

def populateMarket(bettingAgents, lengthOfRace):
    """
    Populate market with betting agents as specified in config file
    """
    def initAgent(name, quantity, id):
        if name == 'Test': return Agent_Test(id, name, lengthOfRace)
        if name == 'Random': return Agent_Random(id, name, lengthOfRace)
        if name == 'Leader_Wins': return Agent_Leader_Wins(id, name, lengthOfRace)
        if name == 'Underdog': return Agent_Underdog(id, name, lengthOfRace)
        if name == 'Back_Favourite': return Agent_Back_Favourite(id, name, lengthOfRace)
        if name == 'Linex': return Agent_Linex(id, name, lengthOfRace)

    id = 0
    for agent in config.agents:
        type = agent[0]
        for i in range(agent[1]):
            bettingAgents[id] = initAgent(agent[0], agent[1], id)
            id = id + 1

def initialiseExchanges(exchanges, exchangeOrderQs):
    """
    Initialise exchanges, returns list of exchange objects
    """
    for i in range(NUM_OF_EXCHANGES):
        exchanges[i] = Exchange(i, NUM_OF_COMPETITORS) # NUM_OF_COMPETITORS may be changed to list of competitor objects that are participating
        exchangeOrderQs[i] = queue.Queue()

def initialiseBettingAgents(bettingAgents, bettingAgentQs, bettingAgentThreads, exchanges, exchangeOrderQs, startTime, numberOfTimesteps, lengthOfRace, event):
    """
    Initialise betting agents
    """
    populateMarket(bettingAgents, lengthOfRace)
    # Create threads for all betting agents that wait until event session
    # has started
    for id, agent in bettingAgents.items():
        bettingAgentQs[id] = queue.Queue()
        thread = threading.Thread(target = agentLogic, args = [agent, bettingAgentQs[id], exchanges, exchangeOrderQs, event, startTime, numberOfTimesteps])
        bettingAgentThreads.append(thread)

def updateRaceQ(bettingAgentQs, timestep):
    """
    Read in race data and update agent queues with competitor distances at timestep
    """
    with open(RACE_DATA_FILENAME, 'r') as file:
        reader = csv.reader(file)
        r = [row for index, row in enumerate(reader) if index == timestep]
    time = r[0][0]
    compDistances = {}
    for c in range(NUM_OF_COMPETITORS):
        compDistances[c] = r[0][c+1]

    # Create update
    update = raceUpdate(time, compDistances)

    for id, q in bettingAgentQs.items():
        q.put(update)

def preRaceBetPeriod(exchanges, startTime):
    print("Start of pre-race betting period, lasting " + str(PRE_RACE_BETTING_PERIOD_LENGTH))
    for i in range(PRE_RACE_BETTING_PERIOD_LENGTH):
        time.sleep(0.01)
    print("End of pre-race betting period")
    # marketUpdates = {}
    # for id, ex in exchanges.items():
    #     timeInEvent = time.time() - startTime
    #     print("Exchange " + str(id) + " markets: ")
    #     print(exchanges[id].publishMarketState(timeInEvent))


def eventSession(simulationId, event, numberOfTimesteps, lengthOfRace, winningCompetitor):
    """
    Set up and management of race event
    """
    # Timestamp
    startTime = time.time()

    # Initialise exchanges
    exchanges = {}
    exchangeOrderQs = {}
    exchangeThreads = []
    initialiseExchanges(exchanges, exchangeOrderQs)

    # Initialise betting agents
    bettingAgents = {}
    bettingAgentQs = {}
    bettingAgentThreads = []
    initialiseBettingAgents(bettingAgents, bettingAgentQs, bettingAgentThreads, exchanges, exchangeOrderQs, startTime, numberOfTimesteps, lengthOfRace, event)

    # Start exchange threads
    for id, exchange in exchanges.items():
        thread = threading.Thread(target = exchangeLogic, args = [exchange, exchangeOrderQs[id], bettingAgentQs, event, startTime, numberOfTimesteps])
        exchangeThreads.append(thread)

    for thread in exchangeThreads:
        thread.start()

    # Start betting agent threads
    for thread in bettingAgentThreads:
        thread.start()

    # Initialise event
    event.set()

    # Pre-race betting period
    preRaceBetPeriod(exchanges, startTime)


    # have loop which runs until competitor has won race
    i = 0
    while(i < numberOfTimesteps):
        updateRaceQ(bettingAgentQs, i+1)
        i = i+1
        if TBBE_VERBOSE: print(i)
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

        time.sleep(0.01)


    # End event
    event.clear()

    # Close threads
    for thread in exchangeThreads: thread.join()
    for thread in bettingAgentThreads: thread.join()

    print("Simulation complete")

    print("Writing data....")
    for id, ex in exchanges.items():
        for orderbook in ex.compOrderbooks:
            for trade in orderbook.tape:
                print(trade)

    # Settle up all transactions over all exchanges
    for id, ex in exchanges.items():
        ex.settleUp(bettingAgents, winningCompetitor)

    # for id, exchange in exchanges.items():
    #     exchange.tapeDump('transactions.csv', 'a', 'keep')

    for id, agent in bettingAgents.items():
        print("Agent " + str(id) + "\'s final balance: " + str(agent.balance))


def main():
    # Simulation attributes
    currentSimulation = 0
    numOfSimulations = 1
    ####################

    # set things up
    # have while loop for running multiple races
    # within loop instantiate competitors into list
    # run simulation and matching engine
    while currentSimulation < numOfSimulations:
        simulationId = "Simulation: " + str(currentSimulation)

        # Create race event data
        race = Simulator(NUM_OF_COMPETITORS)
        race.run()
        numberOfTimesteps = race.numberOfTimesteps
        lengthOfRace = race.race_attributes.length
        winningCompetitor = race.winner

        # Start up thread for race on which all other threads will wait
        event = threading.Event()
        eventSession(simulationId, event, numberOfTimesteps, lengthOfRace, winningCompetitor)

        currentSimulation = currentSimulation + 1






if __name__ == "__main__":
    main()
