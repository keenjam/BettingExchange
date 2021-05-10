# hill climbing search of a one-dimensional objective function
from numpy import asarray
from numpy.random import randn
from numpy.random import rand
from numpy.random import seed
from matplotlib import pyplot
import pandas as pd
import csv

from TBBE import Session

# optimiser can be used to optimise a variety of attributes of a bettor
# in the pursuit of maximising profit;
# for example, the stake of a bet or the odds to bet at

def parseBalance(agentId):
    dataframe = pd.read_csv("data/final_balance_" + str(agentId) + ".csv")
    print(dataframe)
    finalBalance = dataframe.iloc[0][str(agentId)]
    print(finalBalance)
    return finalBalance


# objective function
def stakeObjective(agentId, x):
    # change stake of specified betting agent to be candidate stake 'x'
    print("CANDIDATE")
    print(x[0])
    sess = Session()
    print(sess.bettingAgents[agentId].stake)
    sess.bettingAgents[agentId].stake = x[0]
    print(sess.bettingAgents[agentId].stake)

    sess.runSession()

    finalBalance = parseBalance(agentId)
    print(finalBalance)
    return finalBalance

def deltaObjective(agentId, x):
    # change stake of specified betting agent to be candidate stake 'x'
    print("CANDIDATE")
    print(x[0])
    sess = Session()
    print(sess.bettingAgents[agentId].layDelta)
    sess.bettingAgents[agentId].backDelta = x[0]
    sess.bettingAgents[agentId].layDelta = x[0]
    print(sess.bettingAgents[agentId].layDelta)

    sess.runSession()

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
        writer.writerow(str(best))
        writer.writerow(str(score))
        writer.writerows([scores])

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
    #saveResults(best, score, scores)


def main():
    # id of agent to be optimised
    agentId = 14
    # define range for input
    stakeBounds = asarray([[1.0, 100.0]])
    deltaBounds = asarray([[-5.0, 5.0]])
    # define the total iterations
    n_iterations = 1
    # define the maximum step size
    stake_step_size = 1.0
    delta_step_size = 0.1

    optimise(agentId, deltaBounds, n_iterations, delta_step_size)


if __name__ == "__main__":
    main()
