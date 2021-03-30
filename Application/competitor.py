import random, math, statistics
from system_constants import *

# Competitor Attributes
class CompetitorPreferences:
    def __init__(self):
        self.length = 0
        self.undulation = 0
        self.temperature = 0
        self.randomise()

        self.preference_dict = self.createPreferenceDict()

    def randomise(self):
        self.length = random.randint(MIN_RACE_LENGTH, MAX_RACE_LENGTH)
        self.undulation = random.randint(MIN_RACE_UNDULATION, MAX_RACE_UNDULATION)
        self.temperature = random.randint(MIN_RACE_TEMPERATURE, MAX_RACE_TEMPERATUE)

    def createPreferenceDict(self):
        preference_dict = {
            "length": (self.length - MIN_RACE_LENGTH) / (MAX_RACE_LENGTH - MIN_RACE_LENGTH),
            "undulation": (self.undulation - MIN_RACE_UNDULATION) / (MAX_RACE_UNDULATION - MIN_RACE_UNDULATION),
            "temperature": (self.temperature - MIN_RACE_TEMPERATURE) / (MAX_RACE_TEMPERATUE - MIN_RACE_TEMPERATURE)
        }

        return preference_dict

# Competitor class

class Competitor:
    """ Competitor object """
    def __init__(self, id, race_attributes):
        self.id = id
        self.distance = 0

        self.speed = 0
        self.initVariables()

        self.preferences = CompetitorPreferences()
        self.race_attributes = race_attributes
        self.alignment = self.calculateAlignment()
        self.responsiveness = 1

    def initVariables(self):
        speedLower = random.randint(30, 40)
        speedHigher = random.randint(41, 50)
        self.speed = (speedLower, speedHigher)

    def calculateAlignment(self):
        # CARTESIAN DIFFERENCE
        # diff = 0
        # for key, value in self.race_attributes.race_attributes_dict.items():
        #     diff = diff + (abs(self.preferences.preference_dict.get(key) - value) ** 2)
        # print("DIFF: " + str(diff))
        # return math.sqrt(diff)

        # MEAN of difference
        align = []
        for key, value in self.race_attributes.race_attributes_dict.items():
            diff = abs(self.preferences.preference_dict.get(key) - value)
            align.append(1-diff)
        return statistics.mean(align)
