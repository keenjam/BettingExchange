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
    dataframe.plot(x = "Time", xlabel="Time (s)", y = ys, ylabel="Distance (m)", kind="line")
    plt.savefig('data.raceevent.png')

    plt.show()
    #sns.lineplot( data=dataframe)

def privOddsPlot(filename):
    dataframe = pd.read_csv(filename)
    ys = []
    for i in range(1, NUM_OF_COMPETITORS+1):
        ys.append(i)

    dataframe.plot(x = "Time", y = ys, xlabel = "Time (s)", ylabel = "Log Odds", drawstyle="steps", logy=True)

    # ax = sns.lineplot(x = "Time", y = ys, data = dataframe)
    # ax.plot()
    file = filename[:-3]
    print(file)
    f = file + 'png'
    print(f)
    plt.savefig(f)
    plt.show()

def price_histories(filename):
    dataframe = pd.read_csv(filename)
    print(dataframe)
    ys = []
    for i in range(1, NUM_OF_COMPETITORS+1):
        ys.append(i)

    dataframe.plot(x = "Time", y = ys, xlabel = "Time (s)", ylabel = "Odds", logy=True, drawstyle="steps")

    # ax = sns.lineplot(x = "Time", y = ys, data = dataframe)
    # ax.plot()
    #plt.rcParams.update({'font.size': 22})
    plt.plot()
    #plt.savefig('data/oddsplot4.png')
    plt.show()

def price_spreads(filename):
    dataframe = pd.read_csv(filename)
    print(dataframe)
    ys = []
    for i in range(1, NUM_OF_COMPETITORS+1):
        ys.append(i)

    dataframe.plot(x = "Time", y = ys, xlabel = "Time (s)", ylabel = "Log Price", drawstyle="steps")

    for i in range(NUM_OF_COMPETITORS):
        print("Mean spread for: " + str(i) + ": " + str(dataframe[str(i)].mean()))

    # ax = sns.lineplot(x = "Time", y = ys, data = dataframe)
    # ax.plot()
    #plt.rcParams.update({'font.size': 22})
    plt.plot()
    #plt.savefig('data/oddsplot4.png')
    plt.show()

def histogram(path, time_interval=0.5):
    # Plot code for odds #
    #
    # dataframe = pd.read_csv(filename)
    # ys = []
    # for i in range(1, NUM_OF_COMPETITORS+1):
    #     ys.append(i)

    #####

    df = pd.read_csv(path)
    df.sort_values(by='time')
    bars = [0]
    for index, row in df.iterrows():
        while (row['time'] >= len(bars)*time_interval):
            bars.append(0)
        bars[-1] += 1

    print(bars)

    print()
    print(df.iloc[-1]['time'])
    ax = sns.barplot(np.round(np.arange(0, len(bars)*time_interval, time_interval), 1), bars)
    ax.set(xlabel='Time (s)', ylabel='Num of Transactions')
    ax.set(xticklabels=[])
    ax.set_yscale("log")
    #plt.setp(ax.get_xticklabels()[::10], visible=False)

    plt.savefig('data/volatility.png')
    ax.plot(logy=True)
    #plt.rcParams.update({'font.size': 24})
    plt.show()


def main():
    #racePlotsForDave()
    race_event_file = "data/race_event_core.csv"
    raceEventPlot(race_event_file)
    #
    comp_odds_file = "data/comp_odds_by_41.csv"
    #privOddsPlot(comp_odds_file)
    histogram('data/transactions_0.csv', time_interval=(30/26))
    #price_histories('data/price_histories_0.csv')
    #price_spreads('data/price_spreads_0.csv')



if __name__ == "__main__":
    main()
