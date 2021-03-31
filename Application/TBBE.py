### ~ THREADED BRISTOL BETTING EXCHANGE ~ ###

import sys, math, threading, time, queue, random, csv, config
from betting_agents import *
from race_simulator import Simulator
from exchange import Exchange

def exchangeLogic(exchange):
    print("EXCHANGE")

def agentLogic(id):
    print("AGENT: " + str(id))


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



def initialiseBettingAgents(bettingAgents, bettingAgentThreads):
    """
    Initialise betting agents
    """
    populateMarket(bettingAgents)
    # Create threads for all betting agents that wait until event session
    # has started
    for id, agent in bettingAgents.items():
        print(agent)
        thread = threading.Thread(target = agentLogic, args = [id])
        bettingAgentThreads.append(thread)


def eventSession(simulationId, numOfCompetitors, event):
    """
    Set up and management of race event
    """
    # Timestamp
    startTime = time.time()

    # Initialise exchange
    exchange = Exchange()
    exchangeThread = threading.Thread(target = exchangeLogic, args = [exchange])
    # need order Q (use queue.Queue())

    # Initialise betting agents
    bettingAgents = {}
    bettingAgentThreads = []
    initialiseBettingAgents(bettingAgents, bettingAgentThreads)

    # Start exchange thread
    exchangeThread.start()
    # Start betting agent threads
    for thread in bettingAgentThreads:
        thread.start()
    # Initiate event
    event.set()

    race = Simulator(numOfCompetitors)
    winner = "NA"

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

    # End event and close threads
    event.clear()
    #exchangeThread.join()
    for thread in bettingAgentThreads:
        thread.join()





def main():
    # Race attributes
    numOfCompetitors = 2
    ###################

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
        eventSession(simulationId, numOfCompetitors, event)

        currentSimulation = currentSimulation + 1






if __name__ == "__main__":
    main()
