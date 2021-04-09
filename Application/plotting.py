import matplotlib.pyplot as plt
import seaborn as sns
import csv
import pandas as pd
import statistics
import scipy
import numpy as np
from system_constants import *

def raceEventPlot(filename):
    dataframe = pd.read_csv(filename)
    print(dataframe)
    ys = []
    for i in range(1, NUM_OF_COMPETITORS+1):
        ys.append(i)
    dataframe.plot(x = "Time", y = ys, kind="line")
    plt.show()

























def main():
    race_event_file = "race_event_core.csv"
    raceEventPlot(race_event_file)


if __name__ == "__main__":
    main()
