### Direct flow of Bristol Betting Exchange ###

# Initialise exchange
# Initialise betting agents
# -- betting agents run prediction simulations and submit intial bets
# Initialise ground truth race and move forward one time step

# Inform betting agents of new race state and allow to make new predictions and
# make new bets

# Everytime there is new LOB activity inform betting agents who can then
# update internal variables

#from competitor import *
from race_simulator import Simulator


# class Exchange:

def event_session(numOfCompetitors, lengthOfTrack):
    event = Simulator(numOfCompetitors)
    winner = "NA"

    # round of betting
    #bet(competitors, agents)

    # have loop which runs until competitor has won race
    while(winner == "NA"):
        # run simulation
        event.updateRaceState()
        # call update function of every betting agent
        #updateAgents(competitors, agents)

        for i in range(len(event.competitors)):
            print(str(event.competitors[i]) + " : " +
                 str(event.competitors[i].distance))
            if(event.competitors[i].distance >= event.race_attributes.length):
               winner = event.competitors[i].id

def main():
    # Race attributes
    numOfCompetitors = 2
    lengthOfTrack = 100
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
        event_session(numOfCompetitors, lengthOfTrack)

        currentSimulation = currentSimulation + 1


if __name__ == "__main__":
    main()
