import quandl
import pandas as pd
import json, datetime, os, re
import zipline.api
import sys, urllib, csv
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
	for ticker in tickers:
		try:
			data = quandl.get('YAHOO/' + ticker)
			data.to_csv('data/stocks/' + ticker + '.csv')
		except:
			print(ticker)
			continue


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

