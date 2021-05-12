# hill climbing search of a one-dimensional objective function
from numpy import asarray
from numpy.random import randn
from numpy.random import rand
from numpy.random import seed
from matplotlib import pyplot
import pandas as pd
import csv

from TBBE import BBE
from system_constants import NUM_OF_SIMS

# optimiser can be used to optimise a variety of attributes of a bettor
# in the pursuit of maximising profit;
# for example, the stake of a bet or the odds to bet at

def parseBalance(agentId):
    finalBalance = 0
    for i in range(NUM_OF_SIMS):
        dataframe = pd.read_csv("data/final_balance_" + str(i) + "_"+ str(agentId) + ".csv")
        balance = dataframe.iloc[0][str(agentId)]
        finalBalance += balance

    finalBalance = finalBalance / NUM_OF_SIMS
    return finalBalance


# objective function
def stakeObjective(agentId, x):
    # change stake of specified betting agent to be candidate stake 'x'
    print("CANDIDATE")
    print(x[0])
    bbe = BBE()



    def argFunc(session): session.bettingAgents[agentId].stake = x[0]

    bbe.runSession(argFunc=argFunc)

    finalBalance = parseBalance(agentId)
    print(finalBalance)
    return finalBalance

def deltaObjective(agentId, x):
    # change stake of specified betting agent to be candidate stake 'x'
    print("CANDIDATE")
    print(x[0])
    bbe = BBE()
    def argFunc(session):
        session.bettingAgents[agentId].backDelta = x[0]
        session.bettingAgents[agentId].layDelta = x[0]


    bbe.runSession(argFunc=argFunc)
    if bbe.session:
        print(bbe.session.bettingAgents[agentId].backDelta)
        print(bbe.session.bettingAgents[agentId].layDelta)

    finalBalance = parseBalance(agentId)
    print(finalBalance)
    return finalBalance

# hill climbing local search algorithm
def hillclimbing(agentId, bounds, n_iterations, step_size):
	# generate an initial point
	solution = bounds[:, 0] + rand(len(bounds)) * (bounds[:, 1] - bounds[:, 0])
	# evaluate the initial point
	solution_eval = deltaObjective(agentId, solution)
	# run the hill climb
	scores = list()
	scores.append(solution_eval)
	for i in range(n_iterations):
		# take a step
		candidate = solution + randn(len(bounds)) * step_size
		# evaluate candidate point
		candidate_eval = deltaObjective(agentId, candidate)
		# check if we should keep the new point
		if candidate_eval >= solution_eval:
			# store the new point
			solution, solution_eval = candidate, candidate_eval
			# keep track of scores
			scores.append(solution_eval)
			# report progress
			print('>%d f(%s) = %.5f' % (i, solution, solution_eval))
	return [solution, solution_eval, scores]

def saveResults(best, score, scores):
    fileName = "optimiser_results.csv"

    with open(fileName, 'w', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(scores)

def optimise(agentId, bounds, n_iterations, step_size):
    # perform the hill climbing search
    best, score, scores = hillclimbing(agentId, bounds, n_iterations, step_size)

    print('Done!')
    print('f(%s) = %f' % (best, score))


    # line plot of best scores
    pyplot.plot(scores, '.-')
    pyplot.xlabel('Improvement Number')
    pyplot.ylabel('Evaluation f(x)')
    pyplot.savefig('improvement.png')
    pyplot.show()
    saveResults(best, score, scores)


def main():
    # id of agent to be optimised
    agentId = 13
    # define range for input
    stakeBounds = asarray([[1.0, 100.0]])
    deltaBounds = asarray([[-1.5, 1.5]])
    # define the total iterations
    n_iterations = 3000
    # define the maximum step size
    stake_step_size = 1.0
    delta_step_size = 0.1

    optimise(agentId, deltaBounds, n_iterations, delta_step_size)


if __name__ == "__main__":
    main()
