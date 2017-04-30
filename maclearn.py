from sklearn.ensemble import RandomForestRegressor
import helpers
import numpy as np
import warnings

warnings.simplefilter(action="ignore", category=DeprecationWarning)


def testRandomForest(df):
	helpers.setupDataFiles('data/IBB_monthly.xlsx')
	df = helpers.buildSignalsDataframe()

	df = df.as_matrix()
	x = np.delete(df, 6, axis=1)
	y = np.delete(df, range(6), axis=1)

	trainx = np.delete(x, range(1800, x.shape[0]), axis=0)
	testx = np.delete(x, range(1800), axis=0)

	trainy = np.delete(y, range(1800, x.shape[0]), axis=0)
	testy = np.delete(y, range(1800), axis=0)
	# trainx, testx, trainy, testy = train_test_split(x, y, test_size=0.3)
	# trainx, validatex, trainy, validatey = train_test_split(trainx, trainy, test_size=0.3)

	rf = RandomForestRegressor(n_jobs=-1)
	rf.fit(trainx, trainy)

	ctr = 0
	diff_list = []
	for k in range(testx.shape[0]):
		# if (float(rf.predict(testx[k]) * testy[k]) > 0):
		# if (abs(rf.predict(testx[k]) - testy[k]) / testy[k] < 0.15)
		if testy[k] == 0:
			continue
		if float(rf.predict(testx[k]) * testy[k]) > 0:
			diff_list.append(rf.predict(testx[k]) - testy[k])
			ctr += 1

	print('mean: ', np.mean(diff_list))
	print('variance: ', np.var(diff_list))
	print('std dev: ', np.std(diff_list))
	print('accuracy: ', ctr / testx.shape[0])


def ml_predict(stocks_signals_list):
	helpers.setupDataFiles('data/IBB_monthly.xlsx')
	df = helpers.buildSignalsDataframe()

	df = df.as_matrix()
	x = np.delete(df, 6, axis=1)
	y = np.delete(df, range(6), axis=1)

	trainx = np.delete(x, range(1800, x.shape[0]), axis=0)
	testx = np.delete(x, range(1800), axis=0)

	trainy = np.delete(y, range(1800, x.shape[0]), axis=0)
	testy = np.delete(y, range(1800), axis=0)

	rf = RandomForestRegressor(n_jobs=-1)
	rf.fit(trainx, trainy)

	predictions = []

	# format of stocks_signals_list:
	# [stock_name, sma, ema, rsi, cci, return, sentiment, price_change]
	for stock in stocks_signals_list:
		predictions.append([stock, rf.predict(stock)])

	return predictions
