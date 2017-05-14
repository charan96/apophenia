from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import helpers, pickle
import numpy as np
import warnings, os
from operator import itemgetter

warnings.simplefilter(action="ignore", category=DeprecationWarning)


def tuning(trainx, testx, trainy, testy):
	mylist = []

	# for feat in [x / 100 for x in range(20, 100, 5)]:
	# 	for samp in [y for y in range(20, 100, 10)]:
	# 		rf = RandomForestRegressor(n_jobs=-1, n_estimators=500, max_features='sqrt', min_samples_leaf=samp)
	# 		rf = rf.fit(trainx, trainy)
	# 		mylist.append([feat, samp, rf.score(testx, testy)])
	#
	# 		print(mylist)
	rf = LinearRegression()
	rf = rf.fit(trainx, trainy)

	print(rf.score(testx, testy))


def testRandomForest():
	helpers.setupDataFiles('data/IBB_monthly.xlsx')
	df = helpers.buildSignalsDataframe()

	df = df.as_matrix()
	x = np.delete(df, 6, axis=1)
	y = np.delete(df, range(6), axis=1)

	trainx = np.delete(x, range(int(x.shape[0] * 0.6) - 5, x.shape[0]), axis=0)
	testx = np.delete(x, range(int(x.shape[0] * 0.6)), axis=0)

	trainy = np.delete(y, range(int(x.shape[0] * 0.6) - 5, x.shape[0]), axis=0)
	testy = np.delete(y, range(int(x.shape[0] * 0.6)), axis=0)

	if not os.path.exists('data/randomForest.pickle'):
		feats = 0.2
		samps = 90

		rf = RandomForestRegressor(n_jobs=-1, n_estimators=500, max_features=feats, min_samples_leaf=samps)
		rf = rf.fit(trainx, trainy)

	else:
		with open('data/randomForest.pickle', 'rb') as phandle:
			rf = pickle.load(phandle)

	ctr = 0
	diff_list = []
	for k in range(testx.shape[0]):
		if float(rf.predict(testx[k]) * testy[k]) > 0:
			diff_list.append(rf.predict(testx[k]) - testy[k])
			ctr += 1

	print('mean: ', np.mean(diff_list))
	print('variance: ', np.var(diff_list))
	print('std dev: ', np.std(diff_list))
	print("\n")
	# print("max_features: " + str(feats) + "\tmin_samples_leaf: " + str(samps))
	print('accuracy: ', ctr / testx.shape[0])
	print('score: ', rf.score(testx, testy))


def ml_predict(stocks_signals_list):
	helpers.setupDataFiles('data/IBB_monthly.xlsx')
	df = helpers.buildSignalsDataframe()

	df = df.as_matrix()
	x = np.delete(df, 6, axis=1)
	y = np.delete(df, range(6), axis=1)

	trainx = np.delete(x, range(int(x.shape[0] * 0.6) - 5, x.shape[0]), axis=0)
	testx = np.delete(x, range(int(x.shape[0] * 0.6)), axis=0)

	trainy = np.delete(y, range(int(x.shape[0] * 0.6) - 5, x.shape[0]), axis=0)
	testy = np.delete(y, range(int(x.shape[0] * 0.6)), axis=0)

	if not os.path.exists('data/randomForest.pickle'):
		rf = RandomForestRegressor(n_jobs=-1, n_estimators=500, max_features=0.2, min_samples_leaf=90)
		rf = rf.fit(trainx, trainy)
	else:
		with open('data/random_forest.pickle', 'rb') as phandle:
			rf = pickle.load(phandle)

	predictions = []

	# format of stocks_signals_list:
	# [stock_name, sma, ema, rsi, cci, return, sentiment, price_change]
	for stock_signals in stocks_signals_list:
		predictions.append([stock_signals[0], rf.predict(stock_signals[1:-1])])

	predictions = list(reversed(sorted(predictions, key=itemgetter(1))))

	return predictions
