import helpers
import time

start = time.time()

helpers.setupDataFiles('data/IBB_monthly.xlsx')
helpers.buildSignalsDataframe()

print('Time: ' + str(time.time() - start))
