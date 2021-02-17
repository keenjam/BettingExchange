# Take in race state which is list of competitor
# objects.
# Update state of competitor objects. If whilst
# updating one competitor crosses line then competitor
# has won. If multiple then return one that has
# travelled furthest.
# Therefore only return competitor that has won
# then do check within BBE of size of pool,
# if size is one then that competitor has won

from competitor import *


def updateRaceState(competitors):
    """ Update race state and return as updated list of Competitor objects """
    

def createCompetitors(numOfCompetitors):
    """ Create Competitor objects and return as a list """
    comps = []
    for i in range(numOfCompetitors):
        comps.append(Competitor())

    return comps
