import datetime as dt
import util as ut
import pandas as pd

sd=dt.datetime(2009,1,1)
ed=dt.datetime(2010,1,1)
symbol = "IBM"
sv = 10000

dates = pd.date_range(sd, ed)
prices_all = ut.get_data([symbol], dates)

price = prices_all[symbol]
print price




