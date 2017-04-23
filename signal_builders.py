import pandas as pd
import numpy as np
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)


def getPandasDataframe(ticker):
	df = pd.read_csv('data/stocks/' + ticker + '.csv', index_col=False)
	df.set_index('Date', inplace=True)

	return df


def buildNormalizedSimpleMovingAverage(ticker, date, num_of_days):
	"""
	build simple moving average of num_of_days for ticker normalized to between 0-1 by dividing it by
	closing price on date
	:return: moving average of ticker (float 0-1)
	"""
	df = getPandasDataframe(ticker)

	try:
		loc = df.index.get_loc(date)

		close_prices = [(df.iloc[loc - k])['Adjusted Close'] for k in range(num_of_days) if (loc - k) >= 0]
		moving_avg = float(np.mean(close_prices))

		normalized_moving_avg = float(moving_avg / df.get_value(date, 'Adjusted Close'))

		return normalized_moving_avg

	except Exception:
		return 0


def buildNormalizedExponentialMovingAverage(ticker, date, num_of_days):
	"""
	build exponential moving average of num_of_days for ticker normalized to between 0-1 by dividing it by
	closing price on date
	:return: normalized exponential moving average of ticker (float 0-1)
	"""
	df = getPandasDataframe(ticker)

	try:
		loc = df.index.get_loc(date)

		close_prices = [(df.iloc[loc - k])['Adjusted Close'] for k in range(num_of_days) if (loc - k) >= 0]
		close_prices = list(reversed(close_prices))

		ema = pd.ewma(np.array(close_prices), num_of_days)
		normalized_ema = ema[-1] / df.get_value(date, 'Adjusted Close')

		return normalized_ema

	except Exception:
		return 0


# todo: not sure how to get dif; different array sizes of ema_12 and ema_26
def buildNormalizedMACD(ticker, date):
	df = getPandasDataframe(ticker)

	try:
		loc = df.index.get_loc(date)

		close_prices_12 = [(df.iloc[loc - k])['Adjusted Close'] for k in range(12) if (loc - k) >= 0]
		close_prices_12 = list(reversed(close_prices_12))

		close_prices_26 = [(df.iloc[loc - k])['Adjusted Close'] for k in range(26) if (loc - k) >= 0]
		close_prices_26 = list(reversed(close_prices_26))

		ema_12 = pd.ewma(np.array(close_prices_12), 12)
		ema_26 = pd.ewma(np.array(close_prices_26), 26)

		print(ema_26)
		dif = ema_12 - ema_26
		dea = pd.ewma(np.array(dif), 9)

		macd = dif - dea

		print(close_prices_12)

	except Exception:
		print('exception')


def relativeStrengthIndex(ticker, date, num_of_days):
	"""
	build the relative strength index of the ticker
	:return: relative strength index (float 1-100)
	"""
	df = getPandasDataframe(ticker)

	try:
		loc = df.index.get_loc(date)

		close_prices = [(df.iloc[loc - k])['Adjusted Close'] for k in range(num_of_days) if (loc - k) >= 0]
		close_prices = list(reversed(close_prices))

		gains = [close_prices[k + 1] - close_prices[k] for k in range(num_of_days - 1) if
			   close_prices[k + 1] > close_prices[k]]
		losses = [close_prices[k] - close_prices[k + 1] for k in range(num_of_days - 1) if
			    close_prices[k + 1] < close_prices[k]]

		rel_strength = np.mean(gains) / np.mean(losses)
		rel_strength_index = 100 - (100 / (1 + rel_strength))

		return rel_strength_index

	except Exception:
		return 0


def getTypicalPrice(df, loc, k):
	adjust_factor = (df.iloc[loc - k])['Adjusted Close'] / (df.iloc[loc - k])['Close']

	adjusted_high = (df.iloc[loc - k])['High'] * adjust_factor
	adjusted_low = (df.iloc[loc - k])['Low'] * adjust_factor
	adjusted_close = (df.iloc[loc - k])['Adjusted Close']

	tp = np.mean([adjusted_high, adjusted_low, adjusted_close])

	return tp


def buildCommodityChannelIndex(ticker, date, num_of_days):
	df = getPandasDataframe(ticker)

	try:
		loc = df.index.get_loc(date)

		current_typical_price = getTypicalPrice(df, loc, 0)

		typical_prices_over_n_days = [getTypicalPrice(df, loc, k) for k in range(0, num_of_days) if (loc - k) >= 0]
		typical_prices_over_n_days = list(reversed(typical_prices_over_n_days))

		tp_moving_avg = float(np.mean(typical_prices_over_n_days))
		mdtp = float(np.mean([abs(typical_prices_over_n_days[k] - tp_moving_avg) for k in range(num_of_days)]))

		cci = (current_typical_price - tp_moving_avg) / (0.015 * mdtp)

		return cci

	except Exception as e:
		print(e)
		return 0


# buildCommodityChannelIndex('AGEN', '2004-11-11', 20)
