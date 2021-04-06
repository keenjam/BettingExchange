# Take in race state which is list of competitor
# objects.
# Update state of competitor objects. If whilst
# updating one competitor crosses line then competitor
# has won. If multiple then return one that has
# travelled furthest.
# Therefore only return competitor that has won
# then do check within BBE of size of pool,
# if size is one then that competitor has won


'''

https://royalsocietypublishing.org/doi/10.1098/rsbl.2011.1120
^ horse optimal acceleration and drafting (staying behind other horses for most of race saves 17% of energy)


https://patentimages.storage.googleapis.com/09/75/87/9296ba713a6891/US20080268930A1.pdf
^ patent describing factors for a horse simulator


'''

import random, csv, pandas, time, operator
import numpy as np
from statistics import mean
from system_constants import *
from competitor import Competitor



# Race Attributes
class RaceAttributes:
    def __init__(self):
        self.race_type = ""
        self.length = 0
        self.undulation = 0
        self.temperature = 0
        self.randomise()

        self.race_attributes_dict = self.createAttributeDict()

    def randomise(self):
        self.length = random.randint(MIN_RACE_LENGTH, MAX_RACE_LENGTH)
        self.undulation = random.randint(MIN_RACE_UNDULATION, MAX_RACE_UNDULATION)
        self.temperature = random.randint(MIN_RACE_TEMPERATURE, MAX_RACE_TEMPERATUE)
        if (self.length <= 1445): self.race_type = "short"
        elif (self.length > 1445 and self.length <= 2890): self.race_type = "medium"
        else: self.race_type = "long"


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
        self.raceData = []

        self.finalStretchDist = {"short": 550,
                        "medium": 750,
                        "long": 1000}
        self.finalStretchIncreases = {}

        # Race state details
        self.winner = None
        self.finished = []

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

    def updateEnergy(self, id, increases):
        sortedComps = sorted(self.competitors, key = operator.attrgetter('distance'))
        for i in range(len(sortedComps)-1):
            # EFFECT OF DRAFTING DURING THE RACE
            # 5 and 0.83 chosen as defined by https://royalsocietypublishing.org/doi/10.1098/rsbl.2011.1120
            if sortedComps[i+1].distance <= sortedComps[i].distance + 5:
                sortedComps[i].energy = sortedComps[i].energy - (0.83*increases[sortedComps[i].id])
            else:
                sortedComps[i].energy = sortedComps[i].energy - increases[sortedComps[i].id]

        sortedComps[len(sortedComps)-1].energy = sortedComps[len(sortedComps)-1].energy - increases[sortedComps[len(sortedComps)-1].id]

    def updateResponsiveness(self):
        """ Update responsiveness attribute of all competitors """

        def finalStretch(self, c):
            if c.distance >= self.race_attributes.length - self.finalStretchDist[self.race_attributes.race_type] and c.id not in self.finalStretchIncreases:
                # in final stretch
                distanceLeft = (self.race_attributes.length - c.distance)
                energyLeft = c.energy / distanceLeft
                buildUp = energyLeft / distanceLeft
                self.finalStretchIncreases[c.id] = buildUp

            if c.id in self.finalStretchIncreases:
                c.responsiveness = c.responsiveness + self.finalStretchIncreases[c.id]

        # if race is long then competitors should have lower responsiveness at start and middle with burst at end
        # if race is short then competitors should have resonably consistent responsiveness throughout
        for c in self.competitors:
            finalStretch(self, c)


    def updateRaceState(self):
        """ Update race state by updating distance variable of Competitor objects """
        increases = {}
        for c in self.competitors:
            increase = c.responsiveness * (c.alignment * random.randint(c.speed[0], c.speed[1]))
            increases[c.id] = increase

            c.distance = c.distance + increase
            if c.distance >= self.race_attributes.length:
                if self.winner == None: self.winner = c.id
                self.finished.append(c.id)

        # update competitor attributes
        self.updateEnergy(c.id, increases)
        self.updateResponsiveness()

        self.time_lapsed = time.time() - self.time_lapsed

    def saveRaceState(self, timestamp):
        row = []
        row.append(timestamp)
        for c in self.competitors:
            row.append(c.distance)

        self.raceData.append(row)

    def run(self):
        """ Run and manage race simulation """
        timestamp = 0
        self.saveRaceState(timestamp)
        while len(self.finished) < NUM_OF_COMPETITORS:
            timestamp = timestamp + 1
            self.updateRaceState()
            self.saveRaceState(timestamp)


        self.numberOfTimesteps = len(self.raceData)

        self.writeToFile("core")


    # Write race state to file
    def writeToFile(self, name):
        header = ["Time"]
        for c in self.competitors:
            header.append(str(c.id))

        fileName = "race_event_" + str(name) + ".csv"
        with open(fileName, 'w', newline = '') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(self.raceData)




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
