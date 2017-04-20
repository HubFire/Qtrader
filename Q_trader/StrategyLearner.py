"""
Template for implementing StrategyLearner  (c) 2016 Tucker Balch
"""
from __future__ import division
import datetime as dt
import qlearn as ql
import pandas as pd
import util as ut
import math
import talib
import random as rand
import numpy as np
import sys




class StrategyLearner(object):

    # constructor
    def __init__(self, verbose = True):
        self.verbose = verbose
        self.cur_value=0
        self.cur_cash =0
        self.cur_hold=0
        self.sv = 0
        self.sd=None
        self.ed=None
        self.learner =None
        self.isVisited = np.zeros((30000,3))

    def get_stages(self,min, max, spilts, num):
        step = (max - min) / spilts
        result = (num - min) / step
        result = math.floor(result)
        return int(result)

    def discretize(self,bar,hold,pro):
        isNaN = False
        for i in bar:
            if math.isnan(i):
                isNaN = True
                break
        if isNaN:
            return 0
        cm = self.get_stages(0, 2, 10, bar[2])
        bu = self.get_stages(0,2,10,bar[3]+1)
        bl = self.get_stages(0,2,10,bar[4]+1)
        hold =hold / 500 + 1
        pro = (pro-self.sv)/self.sv
        pr = self.get_stages(0, 4, 10, pro)
        result = pr+bl*10+bu*100+cm*1000+hold*10000
        return int(result)

    def changeState(self, data, date, a):
        index_list = data.index
        index = [i for i, x in enumerate(index_list) if x == date][0]
        curBar = data.iloc[index]
        # randomrate = 0.2
        # if rand.uniform(0.0, 1.0) <= randomrate:
        #     a = rand.randint(0, 2)
        # compute hold  cash  and new value
        if a == 0:  # BUY
            if self.cur_hold == -500:
                self.cur_hold += 1000
                self.cur_cash -= 1000 * curBar[0]
            if self.cur_hold == 0:
                self.cur_hold += 500
                self.cur_cash -= 500 * curBar[0]

            if self.cur_hold == 500:
                a = 2

        if a == 1:  # SELL
            if self.cur_hold == 500:
                self.cur_hold -= 1000
                self.cur_cash += 1000 * curBar[0]
            if self.cur_hold == 0:
                self.cur_hold -= 500
                self.cur_cash += 500 * curBar[0]
            if self.cur_hold == -500:
                a = 2

        if a == 2:  # NOTHING
            pass
        newBar = data.iloc[index + 1]
        newValue = self.cur_cash + self.cur_hold * newBar[0]
        reward = (newValue - self.sv) / self.sv
        self.cur_value = newValue
        return index_list[index + 1], self.cur_hold, reward

    def getNextDate(self,date,date_list):
        k = [i for i, x in enumerate(date_list) if x == date][0]
        if k+1< len(date_list):
           return date_list[k+1]
        else:
            return None

    def train(self,iterations,data):
        learner=self.learner
        sd = data.index[0]
        ed = data.index[-1]
        scores = np.zeros((iterations,1))
        print data.index
        for iterations in range(1,iterations+1):
            print "iterations :{}".format(iterations)
            total_reward = 0
            date = sd
            bar = data.loc[date]
            state = self.discretize(bar,self.cur_hold,self.cur_value)
            action = learner.querysetstate(state)
            self.isVisited[state][action] = 1
            while (date != ed) :
                newDate ,newHold ,reward =self.changeState(data,date,action)
                newBar = data.loc[newDate]
                state = self.discretize(newBar,newHold,self.cur_value)
                action = learner.query(state,reward)
                self.isVisited[state][action] = 1
                date = newDate
                total_reward+= reward
            scores[iterations-1,0] = total_reward
        return np.median(scores),learner

    # this method should create a QLearner, and train it for trading
    def addEvidence(self, symbol = "IBM", \
        sd=dt.datetime(2008,1,1), \
        ed=dt.datetime(2009,1,1), \
        sv = 10000):
        self.sv =sv
        self.cur_value=sv
        self.cur_cash =sv
        self.cur_hold=0
        self.sd=sd
        self.ed=ed

        self.learner = ql.QLearner(num_states=30000, num_actions = 3)
        syms=[symbol]
        dates = pd.date_range(sd, ed)
        prices_all = ut.get_data(syms, dates)  # automatically adds SPY
        prices = prices_all[syms]  # only portfolio symbols
        ma = talib.SMA(prices[symbol].values, timeperiod=10)
        prices["MA"] = ma
        prices["CM"] = ma / prices[symbol]
        upper, middle, lower = talib.BBANDS(prices[symbol].values, timeperiod=10, nbdevup=2, nbdevdn=2, matype=0)
        prices["BU"] = (upper - prices[symbol]) / prices[symbol]
        prices["BL"] = (lower - prices[symbol]) / prices[symbol]
        #print prices
        self.train(1000,prices)
        # add your code to do learning here

        # example usage of the old backward compatible util function

        # prices_SPY = prices_all['SPY']  # only SPY, for comparison later
        # if self.verbose: print prices
        #
        # # example use with new colname
        # volume_all = ut.get_data(syms, dates, colname = "Volume")  # automatically adds SPY
        # volume = volume_all[syms]  # only portfolio symbols
        # volume_SPY = volume_all['SPY']  # only SPY, for comparison later
        # if self.verbose: print volume

    # this method should use the existing policy and test it against new data
    def testPolicy(self, symbol = "IBM", \
        sd=dt.datetime(2009,1,1), \
        ed=dt.datetime(2010,1,1), \
        sv = 10000):

        self.sv = sv
        self.cur_value = sv
        self.cur_cash = sv
        self.cur_hold = 0
        self.sd = sd
        self.ed = ed

        dates = pd.date_range(sd, ed)
        prices_all = ut.get_data([symbol], dates)  # automatically adds SPY

        trades = prices_all[[symbol,]]  # only portfolio symbols
        syms = [symbol]
        prices = prices_all[syms]  # only portfolio symbols
        ma = talib.SMA(prices[symbol].values, timeperiod=10)
        prices["MA"] = ma
        prices["CM"] = ma / prices[symbol]
        upper, middle, lower = talib.BBANDS(prices[symbol].values, timeperiod=10, nbdevup=2, nbdevdn=2, matype=0)
        prices["BU"] = (upper - prices[symbol]) / prices[symbol]
        prices["BL"] = (lower - prices[symbol]) / prices[symbol]

        trades.values[:, :] = 0

        for date in prices.index:
            bar = prices.loc[date]
            state = self.discretize(bar,self.cur_hold,self.cur_value)
            if(self.isVisited[state][0]+self.isVisited[state][1]+self.isVisited[state][2]==0):
                print date,"random"
            a = self.learner.querysetstate(state)
            if a == 0:  # BUY
                if self.cur_hold == -500:
                    self.cur_hold += 1000
                    self.cur_cash -= 1000 * bar[0]
                    trades.at[date, symbol] =1000
                    print date, "BUY 1000","hold {}".format(self.cur_hold)
                if self.cur_hold == 0:
                    self.cur_hold += 500
                    self.cur_cash -= 500 * bar[0]
                    trades.at[date, symbol] = 500
                    print date, "BUY 500","hold {}".format(self.cur_hold)
                if self.cur_hold == 500:
                    a = 2

            if a == 1:  # SELL
                if self.cur_hold == 500:
                    self.cur_hold -= 1000
                    self.cur_cash += 1000 * bar[0]
                    trades.at[date, symbol] = -1000
                    print date, "SELL 1000","hold {}".format(self.cur_hold)
                if self.cur_hold == 0:
                    self.cur_hold -= 500
                    self.cur_cash += 500 * bar[0]
                    trades.at[date, symbol] = -500
                    print date, "SELL 500","hold {}".format(self.cur_hold)
                if self.cur_hold == -500:
                    a = 2

            if a == 2:  # NOTHING
                pass
            self.cur_value= self.cur_cash + self.cur_hold * bar[0]
        print (self.cur_value-self.sv)/self.sv
        trades.to_csv('trades.csv')
        return trades

        #print trades
if __name__=="__main__":
    st=StrategyLearner()
    st.addEvidence()
    trades=st.testPolicy()


