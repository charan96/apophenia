import helpers
import time
import datetime

start = time.time()
print(datetime.datetime.now())

helpers.setupDataFiles('data/IBB_monthly.xlsx')
helpers.buildSignalsDataframe()

print('Time: ' + str(time.time() - start))
