import helpers
import maclearn
import time
import datetime

start = time.time()
print(datetime.datetime.now())

# maclearn.testRandomForest(df)
maclearn.ml_predict(stocks_signals_list)

print('Time: ' + str(time.time() - start))
