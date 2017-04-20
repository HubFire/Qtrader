#!/usr/bin/env python
# encoding: utf-8

#https://www.zhihu.com/question/39951384
#http://ta-lib.org/function.html
from __future__ import division
import talib
import pandas as pd
import datetime as dt
import util as ut
import numpy as np
import math
import sys
isVisited = np.zeros((30000,3))
print sys.getsizeof(isVisited)/1024
# syms=["IBM"]
# sd=dt.datetime(2008,1,1)
# ed=dt.datetime(2009,1,1)
# dates = pd.date_range(sd, ed)
# prices_all = ut.get_data(syms, dates)  # automatically adds SPY
# prices = prices_all[syms]  # only portfolio symbols
# ma = talib.SMA(prices["IBM"].values, timeperiod=10)
# prices["MA"] = ma
# prices["CM"] = ma / prices["IBM"]
# upper, middle, lower = talib.BBANDS(prices["IBM"].values, timeperiod=10, nbdevup=2, nbdevdn=2, matype=0)
# prices["BU"] = (upper - prices["IBM"]) / prices["IBM"]
# prices["BL"] = (lower - prices["IBM"]) / prices["IBM"]
# print prices



