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
    def __init__(self, numOfCompetitors, comps = None, raceAttributes = None):
        self.time_lapsed = 0
        if raceAttributes == None: self.race_attributes = RaceAttributes()
        else: self.race_attributes = raceAttributes
        if SIM_VERBOSE: self.printInitialConditions()
        if comps == None: self.competitors = self.createCompetitors(numOfCompetitors)
        else: self.competitors = comps
        if SIM_VERBOSE: self.printCompPool()
        self.raceData = []

        self.injuredCompetitors = []
        self.raceSplit = {"start": (0, self.race_attributes.length / 3),
                          "middle": (self.race_attributes.length / 3, (self.race_attributes.length / 3) * 2),
                          "end": ((self.race_attributes.length / 3) * 2, self.race_attributes.length)}
        self.runningStyleImpactChanged = []
        self.finalStretchDist = {"short": 550,
                        "medium": 750,
                        "long": 1000}
        self.finalStretchIncreases = {}

        # Race state details
        self.winner = None
        self.winningTimestep = None
        self.finished = []

    ### CLASS FUNCTIONS BELOW ###

    def createCompetitors(self, numOfCompetitors):
        """ Create Competitor objects and return as a list """

        # IMPROVEMENT: ONLY ADD COMPETITOR TO POOL IF SUFFICIENTLY CLOSELY
        # ALIGNED TO RACE CONDIITIONS, ie. create competitor, check alignment,
        # if less than a sys constant variable then don't append- continue loop

        comps = []
        for i in range(numOfCompetitors):
            found = False
            while(found == False):
                c = Competitor(i, self.race_attributes)
                if c.alignment >= 0.95:
                    found = True
            comps.append(c)

        return comps

    def updateEnergy(self, increases):
        sortedComps = sorted(self.competitors, key = operator.attrgetter('distance'))
        for i in range(len(sortedComps)-1):
            if random.randint(0, NUM_OF_COMPETITORS) == i:
                sortedComps[i].energy = sortedComps[i].energy + 50
            # EFFECT OF DRAFTING DURING THE RACE
            # 5 and 0.83 chosen as defined by https://royalsocietypublishing.org/doi/10.1098/rsbl.2011.1120
            if sortedComps[i+1].distance <= sortedComps[i].distance + 5:
                sortedComps[i].energy = sortedComps[i].energy - (0.1*increases[sortedComps[i].id])
            else:
                sortedComps[i].energy = sortedComps[i].energy - increases[sortedComps[i].id]

        sortedComps[len(sortedComps)-1].energy = sortedComps[len(sortedComps)-1].energy - increases[sortedComps[len(sortedComps)-1].id]

    def updateResponsiveness(self):
        """ Update responsiveness attribute of all competitors """

        def injury(self):
            # 1 / 200 chance of 'break down'
            if random.randint(1, 5000) == 666: return True
            else: return False

        def runningStyleImpact(self, c):
            sortedComps = sorted(self.competitors, key = operator.attrgetter('distance'))
            topThird = []
            middleThird = []
            bottomThird = []
            topRange = (int((NUM_OF_COMPETITORS / 3) * 2), NUM_OF_COMPETITORS)
            middleRange = (int((NUM_OF_COMPETITORS / 3)), int((NUM_OF_COMPETITORS / 3) * 2))
            bottomRange = (0, int((NUM_OF_COMPETITORS / 3)))
            for i in range(bottomRange[0], bottomRange[1]): bottomThird.append(sortedComps[i])
            for i in range(middleRange[0], middleRange[1]): middleThird.append(sortedComps[i])
            for i in range(topRange[0], topRange[1]): topThird.append(sortedComps[i])
            if self.raceSplit['start'][0] <= c.distance <= self.raceSplit['start'][1]:
                if c in topThird:
                    if c.running_style == "frontrunner" and c.id not in self.runningStyleImpactChanged:
                        c.responsiveness = c.responsiveness * random.gauss(1.2, 0.05)
                        self.runningStyleImpactChanged.append(c.id)
            if self.raceSplit['middle'][0] <= c.distance <= self.raceSplit['middle'][1]:
                if c in middleThird:
                    if c.running_style == "stalker" and c.id not in self.runningStyleImpactChanged:
                        c.responsiveness = c.responsiveness * random.gauss(1.2, 0.05)
                        self.runningStyleImpactChanged.append(c.id)
                if c.running_style == "frontrunner" and c.id in self.runningStyleImpactChanged:
                    c.responsiveness = c.responsiveness / random.gauss(1.2, 0.05)
                    self.runningStyleImpactChanged.remove(c.id)
            if self.raceSplit['end'][0] <= c.distance <= self.raceSplit['end'][1]:
                if c in bottomThird or c in middleThird:
                    if c.running_style == "closer" and c.id not in self.runningStyleImpactChanged:
                        c.responsiveness = c.responsiveness * random.gauss(1.1, 0.05)
                        self.runningStyleImpactChanged.append(c.id)
                if c.running_style == "stalker" and c.id in self.runningStyleImpactChanged:
                    c.responsiveness = c.responsiveness / random.gauss(1.1, 0.05)
                    self.runningStyleImpactChanged.remove(c.id)


        def finalStretch(self, c):
            if c.distance >= self.race_attributes.length - self.finalStretchDist[self.race_attributes.race_type] and c.id not in self.finalStretchIncreases:
                # in final stretch
                distanceLeft = int(self.race_attributes.length - c.distance)

                energyLeft = int(c.energy / distanceLeft)
                buildUp = energyLeft / distanceLeft
                # multiply buildUp by 2 for more dramatic race events
                self.finalStretchIncreases[c.id] = buildUp * 3

            if c.id in self.finalStretchIncreases:
                c.responsiveness = c.responsiveness + self.finalStretchIncreases[c.id]

        # if race is long then competitors should have lower responsiveness at start and middle with burst at end
        # if race is short then competitors should have resonably consistent responsiveness throughout
        for c in self.competitors:
            if c in self.injuredCompetitors or c in self.finished: continue
            if injury(self) == True:
                c.responsiveness = 0
                self.injuredCompetitors.append(c)
            runningStyleImpact(self, c)
            finalStretch(self, c)

    def calcInterference(self, c, increases):
        # obstruction [0,1]
        blockers = []
        cTempDist = c.distance + increases[c.id]
        for other in self.competitors:
            if other == c or other in self.injuredCompetitors: continue
            otherTempDist = other.distance + increases[other.id]
            if c.distance <= other.distance and c.distance >= other.distance - 5:
                blockers.append((other.id, otherTempDist))

        if len(blockers) == 0: return -1

        numOfBlockers = len(blockers)
        minBlockDist = 1000000
        finalBlockerID = -1
        for b in blockers:
            if b[1] < minBlockDist:
                minBlockDist = b[1]
                finalBlockerID = b[0]

        r = random.randint(NUM_OF_COMPETITORS - numOfBlockers*5, NUM_OF_COMPETITORS)
        if r == NUM_OF_COMPETITORS:
            # distance is not capped
            return -1
        else:
            if SIM_VERBOSE: print(str(c.id) + " is blocked to distance of " + str(minBlockDist) + " from " + str(cTempDist) + " by " + str(finalBlockerID))
            return minBlockDist


    def dynamicDistractions(self, c):
        def stumble():
            if random.randint(1,100) == 50: return float(random.gauss(0.6,0.1))
            else: return 1

        modifier = float(1)
        modifier = modifier * stumble()
        return modifier



    def updateRaceState(self, timestamp):
        """ Update race state by updating distance variable of Competitor objects """
        increases = {}
        for c in self.competitors:
            dynamicDistractions = self.dynamicDistractions(c)
            increase = c.consistency * c.responsiveness * dynamicDistractions * (c.alignment * random.randint(c.speed[0], c.speed[1]))
            increases[c.id] = increase

        winners = []
        for c in self.competitors:
            if c in self.injuredCompetitors or c.id in self.finished: continue
            cappedDist = self.calcInterference(c, increases)
            if cappedDist == -1: c.distance = min(self.race_attributes.length, c.distance + increases[c.id])
            else: c.distance = min(self.race_attributes.length, min(cappedDist, c.distance + increases[c.id]))
            # check if moved into next stage of race
            if c.distance >= self.race_attributes.length:
                if self.winner == None:
                    winners.append(c.id)
                    #self.winner = c.id
                    self.winningTimestep = timestamp
                if c.id not in self.finished: self.finished.append(c.id)

        if len(winners) > 0:
            r = random.randint(0, len(winners)-1)
            self.winner = winners[r]

        # update competitor attributes
        self.updateEnergy(increases)
        self.updateResponsiveness()

        self.time_lapsed = time.time() - self.time_lapsed

    def saveRaceState(self, timestamp):
        row = []
        row.append(timestamp)
        for c in self.competitors:
            row.append(c.distance)

        self.raceData.append(row)

    def run(self, fn):
        """ Run and manage race simulation """
        timestamp = 0
        self.saveRaceState(timestamp)
        while len(self.finished) + len(self.injuredCompetitors) < NUM_OF_COMPETITORS:
            timestamp = timestamp + 1
            self.updateRaceState(timestamp)
            self.saveRaceState(timestamp)


        self.numberOfTimesteps = len(self.raceData)

        if fn != None: self.writeToFile(fn)


    # Write race state to file
    def writeToFile(self, name):
        header = ["Time"]
        for c in self.competitors:
            header.append(str(c.id))

        fileName = "data/race_event_" + str(name) + ".csv"
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
