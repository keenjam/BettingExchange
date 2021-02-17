### Direct flow of Bristol Betting Exchange ###

# Initialise exchange
# Initialise betting agents
## -- betting agents run prediction simulations and submit intial bets
# Initialise ground truth race and move forward one time step

# Inform betting agents of new race state and allow to make new predictions and
# make new bets

# Everytime there is new LOB activity inform betting agents who can then update internal variables

#from competitor import *
from race_simulator import *


# class Exchange:


def main():
    # Race attributes
    numOfCompetitors = 5
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
        # instantiate list of competitor objects
        competitors = createCompetitors(numOfCompetitors)
        updateRaceState(competitors)
        currentSimulation+=1




if __name__ == "__main__":
    main()
