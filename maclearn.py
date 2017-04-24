from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
import numpy as np
import warnings
from sklearn.datasets import load_boston

warnings.simplefilter(action="ignore", category=DeprecationWarning)

boston = load_boston()

df = boston.data
# df_train = np.delete(df, range(403, 503), 0)
# df_test = np.delete(df, range(403), 0)

x = np.delete(df, 12, axis=1)
y = np.delete(df, range(12), axis=1)

# test_X = np.delete(df_test, 12, axis=1)
# test_Y = np.delete(df_test, range(12), axis=1)

rf = RandomForestRegressor()
# rf = AdaBoostRegressor(n_estimators=200)
trainx, testx, trainy, testy = train_test_split(x, y, test_size=0.3)

rf.fit(trainx, trainy)
accuracy = rf.score(testx, testy)

ctr = 0
for k in range(100):
	if (abs(rf.predict(testx[k]) - testy[k])) / testy[k] < 0.1:
		ctr += 1
	print(rf.predict(testx[k]), testy[k], rf.predict(testx[k]) - testy[k],
		abs(rf.predict(testx[k]) - testy[k]) / testy[k])

print(ctr)
print(accuracy)
