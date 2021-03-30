### ~ THREADED BRISTOL BETTING EXCHANGE ~ ###

import sys, math, threading, time, queue, random, csv, config

class BettingAgent:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.balance = 500
        self.orders = {}

class Agent_Test(BettingAgent):
    def hello():
        print("Hello World")
