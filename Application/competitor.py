import random, math, statistics
from system_constants import *

'''

1) Uncertainty on race speed should be different for each competitor as some horses are more reliable than others
2) Alignment methods - cartesian vs mean vs other
3) Normalisation of preferences, currently linear but could try others for more realistic distribution
3) Responsiveness variable - changes over different periods of race -> website with graphs of horse speed over race distances
   -> for more accuracy responsiveness doesn't just kick in a different points due to race length but its impact is different, e.g
      for longer races the differnces in speed will be greater than in shorter race where horse runs flat out for whole distance
4)







'''


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

        # competitor attributes
        #self.class = ""
        self.responsiveness = 1
        self.energy = race_attributes.length
        self.speed = 0
        self.running_style = ""
        self.initVariables()

        self.preferences = CompetitorPreferences()
        self.race_attributes = race_attributes
        self.alignment = self.calculateAlignment()



    def initVariables(self):
        speedLower = random.randint(12, 15)
        speedHigher = random.randint(16, 19)
        self.speed = (speedLower, speedHigher)
        self.running_style = random.choice(["frontrunner", "stalker", "closer"])

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
