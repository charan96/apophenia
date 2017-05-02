import pandas as pd
import numpy as np
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)


def getPandasDataframe(ticker):
	if ticker == 'IBB':
		df = pd.read_csv('data/IBB.csv', index_col=False)
		df.set_index('Date', inplace=True)
	else:
		df = pd.read_csv('data/stocks/' + ticker + '.csv', index_col=False)
		df.set_index('Date', inplace=True)

	return df


def buildNormalizedSimpleMovingAverage(ticker, date, num_of_days):
	"""
	build simple moving average of num_of_days for ticker normalized to between 0-1 by dividing it by
	closing price on date
	:return: moving average of ticker (float)
	"""
	df = getPandasDataframe(ticker)

	try:
		loc = df.index.get_loc(date)

		close_prices = [(df.iloc[loc - k])['Adjusted Close'] for k in range(num_of_days) if (loc - k) >= 0]
		moving_avg = float(np.mean(close_prices))

		normalized_moving_avg = float(moving_avg / df.get_value(date, 'Adjusted Close')) * 100

		if np.isnan(rel_strength_index):
			return 0

		return normalized_moving_avg

	except Exception:
		return 0

# change
def buildNormalizedExponentialMovingAverage(ticker, date, num_of_days):
	"""
	build exponential moving average of num_of_days for ticker normalized to between 0-1 by dividing it by
	closing price on date
	:return: normalized exponential moving average of ticker (float)
	"""
	df = getPandasDataframe(ticker)

	try:
		loc = df.index.get_loc(date)

		close_prices = [(df.iloc[loc - k])['Adjusted Close'] for k in range(num_of_days) if (loc - k) >= 0]
		close_prices = list(reversed(close_prices))

		ema = pd.ewma(np.array(close_prices), num_of_days)
		normalized_ema = (ema[-1] / df.get_value(date, 'Adjusted Close')) * 100

		if np.isnan(rel_strength_index):
			return 0

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

		if np.isnan(rel_strength_index):
			return 0

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
	"""
	build the commodity channel index
	:return: cci or 0
	"""
	df = getPandasDataframe(ticker)

	try:
		loc = df.index.get_loc(date)

		current_typical_price = getTypicalPrice(df, loc, 0)

		typical_prices_over_n_days = [getTypicalPrice(df, loc, k) for k in range(0, num_of_days) if (loc - k) >= 0]
		typical_prices_over_n_days = list(reversed(typical_prices_over_n_days))

		tp_moving_avg = float(np.mean(typical_prices_over_n_days))
		mdtp = float(np.mean([abs(typical_prices_over_n_days[k] - tp_moving_avg) for k in range(num_of_days)]))

		cci = (current_typical_price - tp_moving_avg) / (0.015 * mdtp)

		if np.isnan(rel_strength_index):
			return 0

		return cci

	except Exception:
		return 0


def buildActiveReturn(ticker, date):
	ticker_df = getPandasDataframe(ticker)
	ibb_df = getPandasDataframe('IBB')

	try:
		ticker_loc = ticker_df.index.get_loc(date)
		ibb_loc = ibb_df.index.get_loc(date)

		if (ticker_loc - 250) >= 0:
			month_ago_ticker_price = (ticker_df.iloc[ticker_loc - 20])['Adjusted Close']
			month_ago_ibb_price = (ibb_df.iloc[ibb_loc - 20])['Adj Close']

			year_ago_ticker_price = (ticker_df.iloc[ticker_loc - 250])['Adjusted Close']
			year_ago_ibb_price = (ibb_df.iloc[ibb_loc - 250])['Adj Close']

			ticker_index = month_ago_ticker_price / year_ago_ticker_price
			benchmark_index = month_ago_ibb_price / year_ago_ibb_price

			active_return = ticker_index - benchmark_index

			if np.isnan(rel_strength_index):
				return 0

			return active_return
		else:
			return 0

	except Exception:
		return 0

# todo: change to percent increase
def buildPriceChange(ticker, date, num_of_days):
	df = getPandasDataframe(ticker)

	try:
		loc = df.index.get_loc(date)

		close_prices = [(df.iloc[loc + k])['Adjusted Close'] for k in range(1, num_of_days + 1) if
				    (loc + k) <= df.shape[0]]

		avg_close_prices = np.mean(close_prices)

		avg_price_change = float(avg_close_prices - df.get_value(date, 'Adjusted Close'))

		if np.isnan(rel_strength_index):
			return 0

		return avg_price_change

	except Exception:
		return 0

