# Take in race state which is list of competitor
# objects.
# Update state of competitor objects. If whilst
# updating one competitor crosses line then competitor
# has won. If multiple then return one that has
# travelled furthest.
# Therefore only return competitor that has won
# then do check within BBE of size of pool,
# if size is one then that competitor has won

import random
from statistics import mean
from system_constants import *
from competitor import Competitor

# Race Attributes
class RaceAttributes:
    def __init__(self):
        self.length = 0
        self.undulation = 0
        self.temperature = 0
        self.randomise()

        self.race_attributes_dict = self.createAttributeDict()

    def randomise(self):
        self.length = random.randint(MIN_RACE_LENGTH, MAX_RACE_LENGTH)
        self.undulation = random.randint(MIN_RACE_UNDULATION, MAX_RACE_UNDULATION)
        self.temperature = random.randint(MIN_RACE_TEMPERATURE, MAX_RACE_TEMPERATUE)

    def createAttributeDict(self):
        race_attribute_dict = {
            "length": (self.length - MIN_RACE_LENGTH) / (MAX_RACE_LENGTH - MIN_RACE_LENGTH),
            "undulation": (self.undulation - MIN_RACE_UNDULATION) / (MAX_RACE_UNDULATION - MIN_RACE_UNDULATION),
            "temperature": (self.temperature - MIN_RACE_TEMPERATURE) / (MAX_RACE_TEMPERATUE - MIN_RACE_TEMPERATURE)
        }

        return race_attribute_dict


# Race Simulator

class Simulator:
    """ Race simulator """
    def __init__(self, numOfCompetitors):
        self.time_lapsed = 0
        self.race_attributes = RaceAttributes()
        if SIM_VERBOSE: self.printInitialConditions()
        self.competitors = self.createCompetitors(numOfCompetitors)
        if SIM_VERBOSE: self.printCompPool()

    ### CLASS FUNCTIONS BELOW ###

    def createCompetitors(self, numOfCompetitors):
        """ Create Competitor objects and return as a list """

        # IMPROVEMENT: ONLY ADD COMPETITOR TO POOL IF SUFFICIENTLY CLOSELY
        # ALIGNED TO RACE CONDIITIONS, ie. create competitor, check alignment,
        # if less than a sys constant variable then don't append- continue loop

        comps = []
        for i in range(numOfCompetitors):
            comps.append(Competitor(i, self.race_attributes))

        return comps

    def updateResponsiveness(self):
        """ Update responsiveness attribute of all competitors """
        for c in self.competitors:
            c.responsiveness


    def updateRaceState(self):
        """ Update race state by updating distance variable of Competitor objects """
        for c in self.competitors:
            c.distance = c.distance + c.responsiveness * (c.alignment * random.randint(c.speed[0], c.speed[1]))








    # Documentation functions below

    def printInitialConditions(self):
        conds = self.race_attributes
        print("\n//// INITIAL RACE CONDITIONS ////")
        print("Length: " + str(conds.length) + " , Undulation: " + str(conds.undulation) + " , Temperature: " + str(conds.temperature))
        print(conds.race_attributes_dict)
        print("")

    def printCompPool(self):
        comps = self.competitors
        print("\n//// COMPETITOR POOL ////")
        for c in comps:
            prefs = c.preferences
            print("ID: " + str(c.id) + " Speed: (" + str(c.speed[0]) + ", " + str(c.speed[1]) + ") Preferences -> Length: " + str(prefs.length) + " , Undulation: " + str(prefs.undulation) + " , Temperature: " + str(prefs.temperature))
            print(c.alignment)
            print("")
