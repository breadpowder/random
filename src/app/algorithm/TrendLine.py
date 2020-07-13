import trendln
# this will serve as an example for security or index closing prices, or low and high prices
import yfinance as yf # requires yfinance - pip install yfinance
import matplotlib as plt
tick = yf.Ticker('^GSPC') # S&P500
hist = tick.history(period="2mo", rounding=True)
h = hist[-1000:].Close

mins, maxs = trendln.calc_support_resistance(h)
minimaIdxs, pmin, mintrend, minwindows = trendln.calc_support_resistance((hist[-1000:].Low, None)) #support only
mins, maxs = trendln.calc_support_resistance((hist[-1000:].Low, hist[-1000:].High))
(minimaIdxs, pmin, mintrend, minwindows), (maximaIdxs, pmax, maxtrend, maxwindows) = mins, maxs

fig = trendln.plot_support_resistance(hist[-1000:].Close) # requires matplotlib - pip install matplotlib
plt.savefig('suppres.svg', format='svg')
plt.show()
plt.clf() #clear figure