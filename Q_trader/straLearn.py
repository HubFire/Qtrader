"""
Template for implementing StrategyLearner  (c) 2016 Tucker Balch
"""
from __future__ import division
import datetime as dt
import qlearn as ql
import pandas as pd
import util as ut
import talib
import math
import numpy as np
import random as rand

class StrategyLearner(object):
    def __init__(self, symbol = "IBM", sd=dt.datetime(2008,1,2), ed=dt.datetime(2009,1,1), sv = 10000):
        self.symbol=symbol
        self.sd=sd
        self.ed=ed
        self.sv=sv
        self.data=None
        self.curDate = sd
        self.index = []

        #self.curState = -1
        self.cur_value=sv
        self.cur_cash=sv
        self.cur_hold=0
        self.learner = ql.QLearner(num_states=30000, num_actions = 3)
    # is end date ?
    def isGoal(self,bar):
        pass

    def get_stages(self,min, max, spilts, num):
        step = (max - min) / spilts
        result = (num - min) / step
        result = math.floor(result)
        return int(result)

    def init(self):
        dates = pd.date_range(self.sd, self.ed)
        prices_all = ut.get_data([self.symbol], dates)
        prices = prices_all[[self.symbol]]

        ma = talib.SMA(prices[self.symbol].values, timeperiod=10)
        prices["MA"] = ma
        prices["CM"] = ma / prices[self.symbol]
        upper, middle, lower = talib.BBANDS(prices[self.symbol].values, timeperiod=10, nbdevup=2, nbdevdn=2, matype=0)
        prices["BU"] = (upper - prices["IBM"]) / prices["IBM"]
        prices["BL"] = (lower - prices["IBM"]) / prices["IBM"]
        # prices["hold"]=0
        # prices["cash"]=self.sv
        # prices["value"] = self.sv
        self.data= prices
        print self.data
        self.index = self.data.index
        self.curState= self.discretize(self.data.iloc[0])
        self.changeState(self.curDate,0)
        print self.curState

    # num of states:30000
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
        return result

    # state  from  date to next date
    def changeState(self,date,a):
        index = [i for i ,x in enumerate(self.index) if x==date][0]
        curBar =self.data.iloc[index]
        randomrate = 0.2
        if rand.uniform(0.0,1.0) <=randomrate:
            a= rand.randint(0,2)

        # compute hold  cash  and new value
        if a==0: #BUY
            if self.cur_hold == -500:
                self.cur_hold+=1000
                self.cur_cash-=1000*curBar[0]
            if self.cur_hold ==0:
                self.cur_hold+=500
                self.cur_cash -= 500 * curBar[0]

            if self.cur_hold==500:
                a=2

        if a==1: #SELL
           if self.cur_hold==500:
               self.cur_hold-=1000
               self.cur_cash+=1000*curBar[0]
           if self.cur_hold==0:
               self.cur_hold-=500
               self.cur_cash += 500 * curBar[0]
           if self.cur_hold==-500:
               a=2

        if a==2: #NOTHING
            pass
        newBar = self.data.iloc[index+1]
        newValue = self.cur_cash+self.cur_hold*newBar[0]
        reward = (newValue-self.sv)/self.sv
        self.cur_value=newValue
        return self.index[index+1],self.cur_hold,reward

    def getNextDate(self,date):
        date = pd.to_datetime(date)
        i = [i for i, x in enumerate(self.index) if x == date][0]
        if i+1< len(self.index):
           return self.index[i+1]
        else:
            return None


    def train(self,iterations):
        learner=self.learner
        sd = self.sd
        ed = self.ed
        scores = np.zeros((iterations,1))
        for iterations in range(1,iterations+1):
            total_reward = 0
            date = sd
            bar = self.data.loc[date]
            state = self.discretize(bar,self.cur_hold,self.cur_value)
            action = learner.querysetstate(state)
            while (date != ed) :
                newDate ,newHold ,reward =self.changeState(date,action)
                newBar = self.data.loc[newDate]
                state = self.discretize(newBar,newHold,self.cur_value)
                action = learner.query(state,reward)
                date = newDate
                total_reward+= reward
            scores[iterations-1,0] = total_reward
        return np.median(scores),learner





















if __name__ == "__main__":
   st = StrategyLearner()
   st.init()
   #print st.data
