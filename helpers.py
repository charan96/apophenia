import quandl
import pandas as pd
import json, datetime, os, re
import matplotlib.pyplot as plt
import numpy as np


def getQuandlAPIKey():
	"""
	grabs the API Key of Quandl from the config.txt file
	:return: Quandl API key
	"""
	with open('config.txt', 'r') as infile:
		config = json.load(infile)
		return config['API_key']


# def makeURL(ticker, options):
# 	return 'http://download.finance.yahoo.com/d/quotes.csv?s=' + ticker + '&f=' + options


# def getStockDatasetsFromYahooFinance(tickers_list):
# 	options = 'ohlcv'
# 	for ticker in tickers_list:
# 		requestURL = makeURL(ticker, options)
# 		urllib.request.urlretrieve(requestURL, 'data/stocks/' + ticker + '.csv')


def convertToMonthYearString(datetime_object):
	"""
	convert datetime object to mth-year string
	:rtype: string
	"""
	return datetime.datetime.strftime(datetime_object, '%m-%Y')


def cleanTickers(tickers):
	clean_tickers = [re.search('([A-Z])\w+', ticker).group(0) for ticker in tickers]
	return clean_tickers


def makeStockCSVFileFromXLSX(xlsx_file):
	"""
	read in XLSX file and make CSV file with formatted dates and tickers with 1 if ticker in month else 0
	:rtype: None
	"""
	df = pd.read_excel(xlsx_file, index_col=False)

	df.fillna('0', inplace=True)
	df.replace(1.0, '1', inplace=True)
	df.drop(df.index[[0, len(df.index) - 1]], inplace=True)

	cols = list(df.columns)
	cols[1:] = [convertToMonthYearString(cols[x]) for x in range(1, len(cols))]

	df.columns = cols

	tickers = list(df[df.columns[0]])
	tickers = cleanTickers(tickers)
	df[df.columns[0]] = tickers

	df.to_csv('data/IBB_components.csv', index=False)


def getComponentsPandasDataframe():
	"""
	read in the CSV file as dataframe and return it
	:rtype: pandas dataframe
	"""
	df = pd.read_csv('data/IBB_components.csv', index_col=False)
	return df


def getDatasetsFromQuandl(tickers):
	quandl.ApiConfig.api_key = getQuandlAPIKey()
	not_found_tickers = []
	for ticker in tickers:
		# TODO: remove if statement
		if not os.path.exists('data/stocks/' + ticker + '.csv'):
			try:
				data = quandl.get('YAHOO/' + ticker)
				data.to_csv('data/stocks/' + ticker + '.csv')
			except Exception as e:
				not_found_tickers.append(ticker)
				continue

	return not_found_tickers


# def makeHistogram(not_found_tickers):
# 	full_df = getComponentsPandasDataframe()
# 	all_tickers = list(full_df[full_df.columns[0]])
#
# 	dates = [list(full_df.columns)[x] for x in range(1, len(list(full_df.columns)))]
# 	all_tickers_freq = [full_df[date].value_counts()[1] for date in dates]

# Build dataframe without not found stock tickers
# edited_df = getComponentsPandasDataframe()
# for x in not_found_tickers:
# 	edited_df = edited_df[edited_df['Ticker'] != x]
#
# found_ticker_freq = [edited_df[date].value_counts()[1] for date in dates]
#
# plt.bar(range(0, len(dates)), all_tickers_freq, color='b')
# plt.bar(range(0, len(dates)), found_ticker_freq, color='r')
# plt.legend()
#
# differences = [all_tickers_freq[x] - found_ticker_freq[x] for x in range(0, 127)]
# avg = sum(differences) / 127
# mini = min(differences)
# maxi = max(differences)
# print("Avg: " + str(avg) + "\nMin: " + str(mini) + "\nMax: " + str(maxi))
# plt.show()


def setupDataFiles(xlsx_file):
	"""
	create the CSV if doesn't exist and grab the historical data for all the stocks
	in the CSV file and put it into the data/stocks directory

	one stop function to set up all the data files
	:rtype: None
	"""
	if not os.path.exists('data/IBB_components.csv'):
		makeStockCSVFileFromXLSX(xlsx_file)

	df = getComponentsPandasDataframe()
	tickers = list(df[df.columns[0]])

	not_found_tickers = getDatasetsFromQuandl(tickers)


# 	makeHistogram(not_found_tickers)


def getFoundTickers():
	found_tickers = [file.split('.')[0] for file in os.listdir('data/stocks/')]

	return found_tickers


def getStockReturn():
	return 100


def getPriceIncrease():
	return 200


def setupReturnsDataframe():
	df = getComponentsPandasDataframe()
	df.set_index('Ticker', inplace=True)
	df = df.transpose()

	data_dict = {}
	found_tickers = getFoundTickers()

	for index, row in df.iterrows():
		for i, item in enumerate(row):
			if (item == 1) and (df.columns[i] in found_tickers):
				if index not in data_dict:
					data_dict[index] = {}
				data_dict[index][df.columns[i]] = [getStockReturn(), getPriceIncrease()]

		if index in data_dict:
			data_dict[index]['avg'] = [int(np.mean([x[0] for x in list(data_dict[index].values())])),
							   int(np.mean([x[1] for x in list(data_dict[index].values())]))]
		# print([x[0] for x in list(data_dict[index].values())])

	dataframe = pd.DataFrame({'return': [data_dict[x]['avg'][0] for x in sorted(list(data_dict.keys()))]},
					 index=sorted(list(data_dict.keys())))
	print(data_dict)


def buildSignals():
	setupReturnsDataframe()
