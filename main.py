import helpers
import maclearn
import signal_builders
import time
import datetime

start = time.time()
print(datetime.datetime.now())


# maclearn.testRandomForest(df)


stockSignalsList = []

for ticker in bundle:
	stockSignalsList.append(helpers.createStockList(ticker, date))

maclearn.ml_predict(stockSignalsList)

print('Time: ' + str(time.time() - start))
