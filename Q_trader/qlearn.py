#!/usr/bin/env python
# encoding: utf-8
"""
Template for implementing QLearner  (c) 2015 Tucker Balch
"""

import numpy as np
import random as rand
from numpy import random

class QLearner(object):

    def __init__(self, num_states=100, num_actions = 4, alpha = 0.2, gamma = 0.9, rar = 0.5,
                 radr = 0.99, dyna = 0, verbose = False):

        self.verbose = verbose
        self.num_actions = num_actions
        self.num_states = num_states
        self.alpha = alpha
        self.gamma = gamma
        self.rar = rar
        self.radr = radr
        self.dyna = dyna
        self.s = 0
        self.a = 0
        #初始化Q表,-1到1
        #self.Q = 2 * random.random(size=(num_states, num_actions))-1
        self.Q = np.zeros((num_states,num_actions))


    def querysetstate(self, s):
        """
        @summary: Update the state without updating the Q-table
        @param s: The new state
        @returns: The selected action
        """


        if rand.uniform(0.0, 1.0) < self.rar:
            action = rand.randint(0, self.num_actions - 1)
        else:
            action = np.argmax(self.Q[s])   # 获得当前最优的行为

        self.s = s
        self.a = action

        #if self.verbose:
        #print "s =", s, "a =", action
        return action

    # 返回action，且更新表
    def query(self, s_prime, r):
        """
        @summary: Update the Q table and return an action
        @param s_prime: The new state
        @param r: The ne state
        @returns: The selected action
        """
        self.rar=self.radr*self.rar
        if rand.uniform(0.0, 1.0) < self.rar:
            action_prime = rand.randint(0, self.num_actions - 1)
        else:
            action_prime = np.argmax(self.Q[s_prime])
        # 更新Q表
        self.Q[self.s][self.a] = (1-self.alpha) * self.Q[self.s][self.a] \
            + self.alpha * (r+self.gamma*self.Q[s_prime][action_prime])
        self.a = action_prime
        self.s = s_prime
        #if self.verbose:
        #print "s =", s_prime, "a =", action_prime, "r =", r
        return action_prime





if __name__=="__main__":
    print "Remember Q from Star Trek? Well, this isn't him"
