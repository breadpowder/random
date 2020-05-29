from ib_insync import *
import time
from data.ib_dataFetch import IBDataFetch
# util.startLoop()  # uncomment this line when in a notebook

ib = IB()
ib.connect('127.0.0.1', 7496, clientId=1)
fetch = IBDataFetch(ib)

""""
accS = ib.accountSummary('')

for acc in accS:
    print(acc)


poss = ib.positions()
for pos in poss:
    print(pos)

pnl = ib.reqPnL('')
while True:
    time.sleep(5)
    print(pnl)


fetch.readTicker("Tickers")
"""


contract = Forex('EURUSD')
bars = ib.reqHistoricalData(
    contract, endDateTime='', durationStr='30 D',
    barSizeSetting='1 hour', whatToShow='MIDPOINT', useRTH=True)

# convert to pandas dataframe:
df = util.df(bars)

fetch.writeToDB(df)

print(df)


