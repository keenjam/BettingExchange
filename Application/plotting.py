import matplotlib.pyplot as plt
import seaborn as sns
import csv
import pandas as pd
import statistics
import scipy
import numpy as np
from system_constants import *

def racePlotsForDave():
    for i in range(NUM_OF_SIMS):
        filename = "data/race_event_" + str(i) + ".csv"
        dataframe = pd.read_csv(filename)
        ys = []
        for i in range(1, NUM_OF_COMPETITORS+1):
            ys.append(i)
        dataframe.plot(x = "Time", y = ys, kind="line")
        plt.show()


def raceEventPlot(filename):
    dataframe = pd.read_csv(filename)
    print(dataframe)
    ys = []
    for i in range(1, NUM_OF_COMPETITORS+1):
        ys.append(i)
    dataframe.plot(x = "Time", y = ys, kind="line")
    plt.show()
    #sns.lineplot( data=dataframe)

def privOddsPlot(filename):
    dataframe = pd.read_csv(filename)
    ys = []
    for i in range(1, NUM_OF_COMPETITORS+1):
        ys.append(i)
    dataframe.plot(x = "Time", y = ys, drawstyle="steps")
    plt.show()





def main():
    #racePlotsForDave()
    race_event_file = "data/race_event_core.csv"
    raceEventPlot(race_event_file)

    comp_odds_file = "data/comp_odds_by_14.csv"
    privOddsPlot(comp_odds_file)


if __name__ == "__main__":
    main()
