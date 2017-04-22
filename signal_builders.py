import pandas as pd
import numpy as np


def getStockReturn(ticker, date):
	return 200


def buildNormalizedSimpleMovingAverage(ticker, date, num_of_days):
	"""
	build moving average of num_of_days for ticker
	:return: moving average of ticker (float)
	"""
	df = pd.read_csv('data/stocks/' + ticker + '.csv', index_col=False)
	df.set_index('Date', inplace=True)

	try:
		loc = df.index.get_loc(date)

		close_prices = [(df.iloc[loc - k])['Adjusted Close'] for k in range(num_of_days) if (loc - k) >= 0]
		moving_avg = float(np.mean(close_prices))

		normalized_moving_avg = float(moving_avg / df.get_value(date, 'Adjusted Close'))

		return normalized_moving_avg

	except Exception:
		return 0


def buildExponentialMovingAverage(ticker, date, num_of_days):
	df = pd.read_csv('data/stocks/' + ticker + '.csv', index_col=False)
	df.set_index('Date', inplace=True)

	try:
		loc = df.index.get_loc(date)

		close_prices = [(df.iloc[loc - k])['Adjusted Close'] for k in range(num_of_days) if (loc - k) >= 0]
		close_prices = list(reversed(close_prices))

		ema = pd.ewma(np.array(close_prices), num_of_days)
		normalized_ema = ema[-1] / df.get_value(date, 'Adjusted Close')

		return normalized_ema

	except Exception:
		return 0
