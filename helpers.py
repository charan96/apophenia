import quandl
import pandas as pd
import json, datetime, os
import sys
import numpy as np


def getQuandlAPIKey():
	"""
	grabs the API Key of Quandl from the config.txt file
	:return: Quandl API key
	"""
	with open('config.txt', 'r') as infile:
		config = json.load(infile)
		return config['API_key']


def getStockDatasetsFromQuandl(stocklist_file):
	"""
	gets the historical stock price data for each stock in the file list and creates data files in data directory
	:param stocklist_file: location of file containing list of stock tickers
	"""
	quandl.ApiConfig.api_key = getQuandlAPIKey()

	with open(stocklist_file, 'r') as infile:
		for line in infile:
			for ticker in line.split(',')[1:]:
				ticker = ticker.rstrip('\n')
				if not os.path.exists('data/stocks/' + ticker + '.csv'):
					data = quandl.get('WIKI/' + ticker)
					data.to_csv('data/stocks/' + ticker + '.csv')


def setup_dataframe():
	start_date = datetime.datetime.strptime('02/20/2007', '%m/%d/%Y')
	dataframe = pd.DataFrame()
	with open('data/date_reference.txt', 'r') as dateref, open('data/dow_change_days_list.txt', 'r') as dowfile, open(
		    'data/10year_dow_components.csv', 'w') as outfile:
		dowfile_lines = dowfile.readlines()
		counter = 0
		base_date = datetime.datetime.strptime(dowfile_lines[counter].split(',')[0], '%m/%d/%Y')
		next_date = datetime.datetime.strptime(dowfile_lines[counter + 1].split(',')[0], '%m/%d/%Y')

		for date_string in dateref:
			date_string = date_string.rstrip("\n")
			date = datetime.datetime.strptime(date_string, '%m/%d/%Y')
			if date < next_date and date > base_date:
				outfile.write(date_string + ',' + dowfile_lines[counter].split(',', 1)[1])
			elif date == next_date:
				outfile.write(date_string + ',' + dowfile_lines[counter + 1].split(',', 1)[1])
				base_date = next_date
				if (counter + 2) <= len(dowfile_lines) - 1:
					counter = counter + 1
					next_date = datetime.datetime.strptime(dowfile_lines[counter + 1].split(',')[0],
											   '%m/%d/%Y')
				else:
					next_date = datetime.datetime.today()
					counter = counter + 1
