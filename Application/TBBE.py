### ~ THREADED BRISTOL BETTING EXCHANGE ~ ###

import sys, math, threading, time, queue, random, csv, config
from system_constants import NUM_OF_EXCHANGES, NUM_OF_COMPETITORS
from betting_agents import *
from race_simulator import Simulator
from exchange import Exchange

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
                # COULD BE MODIFIED TO BE A SPECIAL UPDATE-MESSAGE CLASS (protocol)
                q.put([trade, order, markets])

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
        timeInEvent = (time.time() - startTime) * numberOfTimesteps
        order = None
        trade = None

        while agentQ.empty() is False:
            [trade, order, market] = agentQ.get(block = False)
            if trade['backer'] == agent.id: agent.bookkeep(trade, order, timeInEvent)
            if trade['layer'] == agent.id: agent.bookkeep(trade, order, timeInEvent)

        marketUpdates = {}
        for i in range(NUM_OF_EXCHANGES):
            marketUpdates[i] = exchanges[i].publishMarketState(timeInEvent)

        agent.respond(timeInEvent, marketUpdates, trade)
        order = agent.getorder(timeInEvent, marketUpdates)
        #print("ORDER: " + str(order))

        if order != None:
            print(order)
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

def initialiseExchanges(exchanges, exchangeOrderQs):
    """
    Initialise exchanges, returns list of exchange objects
    """
    for i in range(NUM_OF_EXCHANGES):
        exchanges[i] = Exchange(i, NUM_OF_COMPETITORS) # NUM_OF_COMPETITORS may be changed to list of competitor objects that are participating
        exchangeOrderQs[i] = queue.Queue()

def initialiseBettingAgents(bettingAgents, bettingAgentQs, bettingAgentThreads, exchanges, exchangeOrderQs, startTime, numberOfTimesteps, event):
    """
    Initialise betting agents
    """
    populateMarket(bettingAgents)
    # Create threads for all betting agents that wait until event session
    # has started
    for id, agent in bettingAgents.items():
        bettingAgentQs[id] = queue.Queue()
        thread = threading.Thread(target = agentLogic, args = [agent, bettingAgentQs[id], exchanges, exchangeOrderQs, event, startTime, numberOfTimesteps])
        bettingAgentThreads.append(thread)


def eventSession(simulationId, event):
    """
    Set up and management of race event
    """

    race = Simulator(NUM_OF_COMPETITORS)
    numberOfTimesteps = race.race_attributes.length
    winner = "NA"

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
    initialiseBettingAgents(bettingAgents, bettingAgentQs, bettingAgentThreads, exchanges, exchangeOrderQs, startTime, numberOfTimesteps, event)

    # Start exchange threads
    for id, exchange in exchanges.items():
        thread = threading.Thread(target = exchangeLogic, args = [exchange, exchangeOrderQs[id], bettingAgentQs, event, startTime, numberOfTimesteps])
        exchangeThreads.append(thread)

    for thread in exchangeThreads:
        thread.start()

    # Start betting agent threads
    for thread in bettingAgentThreads:
        thread.start()
    # Initiate event
    event.set()

    # round of betting
    #bet(competitors, agents)

    # have loop which runs until competitor has won race
    while(winner == "NA"):
        # run simulation
        race.updateRaceState()
        # call update function of every betting agent
        #updateAgents(competitors, agents)

        for i in range(len(race.competitors)):
            #print(str(race.competitors[i]) + " : " +
                 #str(race.competitors[i].distance))
            if(race.competitors[i].distance >= race.race_attributes.length):
               winner = race.competitors[i].id
               print("WINNER: " + str(winner))

        time.sleep(0.01)

    # End event
    event.clear()
    # Give time for threads to register end of event
    #time.sleep(1)
    # Close threads
    for thread in exchangeThreads: thread.join()
    for thread in bettingAgentThreads: thread.join()

    print("Simulation complete")

    print("Writing data....")
    for id, exchange in exchanges.items():
        exchange.tapeDump('transactions.csv', 'a', 'keep')


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

        # Start up thread for race on which all other threads will wait
        event = threading.Event()
        eventSession(simulationId, event)

        currentSimulation = currentSimulation + 1






if __name__ == "__main__":
    main()
