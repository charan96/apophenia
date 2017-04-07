import quandl
import pandas as pd
import json, datetime, os, re, sys, pickle
import matplotlib.pyplot as plt
import numpy as np
import copy

missing_vals = []


def getFromConfig(key):
	"""
	read the config.json file and return value of the key
	:param key: key for the JSON object
	:return: the value of the key from config.json file
	"""
	with open('config.json', 'r') as infile:
		config = json.load(infile)
		return config[key]


def getQuandlAPIKey():
	"""
	grabs the API Key of Quandl from the config.json file
	:return: Quandl API key
	"""
	return getFromConfig('API_key')


def convertToMonthYearString(datetime_object):
	"""
	convert datetime object to mth-year string
	:rtype: string
	"""
	return datetime.datetime.strftime(datetime_object, '%m-%Y')


def cleanTickers(tickers):
	"""
	remove unnecessary characters and clean tickers from XLSX file
	:param tickers: list of unclean tickers
	:return: list of clean tickers
	"""
	clean_tickers = [re.search('([A-Z])\w+', ticker).group(0) for ticker in tickers]
	return clean_tickers


def getComponentsPandasDataframe():
	"""
	read in the CSV file as dataframe and return it after changing date format
	:rtype: pandas dataframe
	"""
	df = pd.read_csv(getFromConfig('CSV_FILE'), index_col=False)
	cols = list(df.columns)
	updated_cols = ['Ticker', ]
	for date in cols[1:]:
		formatted_date = '-'.join([date.split('-')[1], date.split('-')[0]])
		updated_cols.append(formatted_date)

	df.columns = updated_cols

	return df


def getFoundTickers():
	"""
	get the list of all the tickers that were found by Quandl
	:return: list of tickers that were found by Quandl
	"""
	found_tickers = [file.split('.')[0] for file in os.listdir('data/stocks/')]

	return found_tickers


def makeStockCSVFileFromXLSX(xlsx_file):
	"""
	read in XLSX file and make CSV file with formatted dates and tickers with 1 if ticker in month else 0
	:rtype: None
	"""
	df = pd.read_excel(xlsx_file, index_col=False)

	df.fillna('0', inplace=True)
	df.replace(1.0, '1', inplace=True)
	df.replace(r'\s+', 0, regex=True, inplace=True)
	df.drop(df.index[[0, len(df.index) - 1]], inplace=True)

	cols = list(df.columns)
	cols[1:] = [convertToMonthYearString(cols[x]) for x in range(1, len(cols))]

	df.columns = cols

	tickers = list(df[df.columns[0]])
	tickers = cleanTickers(tickers)
	df[df.columns[0]] = tickers

	df.to_csv(getFromConfig('CSV_FILE'), index=False)


def getDatasetsFromQuandl(tickers):
	"""
	get the dataset for all tickers from Quandl and save the data into CSV files in data/stocks/ folder;
	if ticker not found add to list of not_found_tickers

	:param tickers: list of tickers
	:return not_found_tickers: list of all the tickers that were not found by Quandl
	"""
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


# NOTE: work on final line of the function
def setupDataFiles(xlsx_file):
	"""
	create the CSV if doesn't exist and grab the historical data for all the stocks
	in the CSV file and put it into the data/stocks directory

	one stop function to set up all the data files
	:rtype: None
	"""
	if not os.path.exists(getFromConfig('CSV_FILE')):
		makeStockCSVFileFromXLSX(xlsx_file)

	df = getComponentsPandasDataframe()
	tickers = list(df[df.columns[0]])

	not_found_tickers = getDatasetsFromQuandl(tickers)


def getStockReturn(ticker, date):
	df = pd.read_csv('data/stocks/' + ticker + '.csv', index_col=False)
	df.set_index('Date', inplace=True)

	try:
		loc = df.index.get_loc(date)

		previous_day_close = (df.iloc[loc - 1])['Close']
		current_day_close = df.get_value(date, 'Close')
		return_value = float((current_day_close - previous_day_close) / previous_day_close)

		return return_value

	except Exception:
		missing_vals.append([ticker, date])
		return 0


def getPriceIncrease(ticker, date):
	return 200


def expandDictionaryWithDates(data_dict):
	"""
	add all dates from dates.txt to fill data_dict and remove just months from data_dict
	:param data_dict: data_dict dictionary structure
	:return: updated data dictionary
	"""
	with open(getFromConfig('dates'), 'r') as datefile:
		for date in datefile:
			date = date.rstrip("\n")
			year_month = '-'.join([date.split('-')[0], date.split('-')[1]])
			if year_month in data_dict:
				data_dict[date] = copy.deepcopy(data_dict[year_month])
			else:
				print(year_month)

	for date in list(data_dict.keys()):
		if re.match('^[0-9]{4}\-[0-9]{2}$', date):
			del data_dict[date]

	return data_dict


def prettyPrintDict(data_dict):
	"""
	print the data_dict in a nice viewable format
	:param data_dict: the data_dict dictionary with all the values
	"""
	for key in sorted(data_dict.keys()):
		print("data_dict[" + key + "] = " + str(data_dict[key]))


def addAverageValueInDataDict(date, data_dict):
	"""
	data_dict =	{
		   	    'date(1)': {'ticker1': [sig1, sig2, ... ], ... , 'avg': [avg-of-sig1-on-date1, avg-of-sig2-on-date1, ... ]},
		   	    'date(2)': {'ticker1': [sig1, sig2, ... ], ... , 'avg': [avg-of-sig1-on-date2, avg-of-sig2-on-date2, ... ]},
		   	    ...
		   	    'date(n)': {'ticker1': [sig1, sig2, ... ], ... , 'avg': [avg-of-sig1-on-daten, avg-of-sig2-on-daten, ... ]}
			}
	:param date: date string
	:return: data_dict with average signals of all stocks
	"""
	num_of_signals = getFromConfig('num_of_signals')

	data_dict[date]['avg'] = [float(np.mean([x[k] for x in data_dict[date].values() if float(x[k]) != float(0)])) for
					  k in range(num_of_signals)]

	# NOTE: above line is code equivalent to the following code block
	# signal_value_list = []
	# avg_values = []
	# for index in range(num_of_signals):
	# 	for signal_value in data_dict[date].values():
	# 		if signal_value[index] != float(0):
	# 			signal_value_list.append(signal_value[index])
	#
	# 	avg_values.append(float(np.mean(signal_value_list)))
	#
	# data_dict[date]['avg'] = avg_values

	return data_dict


def setupDataDictionaryStructure(df, data_dict):
	"""
	set up the dictionary with the following structure:
	data_dict =	{
		   	    'year-month(1)': {'ticker1': [None, None, ... ], 'ticker2': [None, None, ... ], ... , 'tickern': [None, None, ... ]},
		   	    'year-month(2)': {'ticker1': [None, None, ... ], 'ticker2': [None, None, ... ], ... , 'tickern': [None, None, ... ]},
		   	    ...
		   	    'year-month(n)': {'ticker1': [None, None, ... ], 'ticker2': [None, None, ... ], ... , 'tickern': [None, None, ... ]}
			}

	The None values are temporary values that will be replaced with signals in populateWithData

	:param df: transpose pandas dataframe of the CSV i.e, row headers: dates and column headers: tickers
	:param data_dict: empty data_dictionary
	:return: data_dictionary with structure setup
	"""
	found_tickers = getFoundTickers()
	num_of_signals = getFromConfig('num_of_signals')  # NOTE: Change value in config.json to change number of signals

	for date, row in df.iterrows():
		for i, item in enumerate(row):
			if ((item == 1) or (item == '1')) and (df.columns[i] in found_tickers):
				ticker = df.columns[i]
				if date not in data_dict:
					data_dict[date] = {}
				data_dict[date][ticker] = [None] * num_of_signals

	return data_dict


def addLegendToDataDict(date, data_dict):
	"""
	add legend with names of the signals
	:return: updated data_dict
	"""
	signal_names = ['return']
	data_dict[date]['legend'] = signal_names

	return data_dict


def populateDataframeWithSignals(data_dict):
	"""
	replace the None values from data_dict with actual signals
	:param data_dict: data_dictionary structure
	:return: data_dict with all signals and avg element in it
	"""
	for date in sorted(list(data_dict.keys())):
		for ticker in data_dict[date]:
			data_dict[date][ticker] = [getStockReturn(ticker, date), getPriceIncrease(ticker, date)]

		addAverageValueInDataDict(date, data_dict)
		addLegendToDataDict(date, data_dict)

	return data_dict


def saveDataDict(data_dict):
	with open('data/data_dict.pickle', 'wb') as phandle:
		pickle.dump(data_dict, phandle, protocol=pickle.HIGHEST_PROTOCOL)

	with open('data/data_dict.json', 'w') as jhandle:
		json.dump(data_dict, jhandle)


# NOTE: temporary functions, remove later
# NOTE: ---------------------------------

def printJSONDatadict():
	with open('data/data_dict.json', 'r') as fhandle:
		data_dict = json.load(fhandle)

	prettyPrintDict(data_dict)


def printPickleDatadict():
	with open('data/data_dict.pickle', 'rb') as fhandle:
		data_dict = pickle.load(fhandle)

	prettyPrintDict(data_dict)


# NOTE: ---------------------------------
# NOTE: temporary functions, remove later

def buildSignalsDataframe():
	df = getComponentsPandasDataframe()
	df.set_index('Ticker', inplace=True)
	df = df.transpose()

	# df.to_html('data/file.html')

	data_dict = {}

	data_dict = setupDataDictionaryStructure(df, data_dict)
	data_dict = expandDictionaryWithDates(data_dict)
	data_dict = populateDataframeWithSignals(data_dict)

	saveDataDict(data_dict)

	dataframe = pd.DataFrame({'return': [data_dict[x]['avg'][0] for x in sorted(list(data_dict.keys()))]},
					 index=sorted(list(data_dict.keys())))

	prettyPrintDict(data_dict)

	# print(dataframe)
