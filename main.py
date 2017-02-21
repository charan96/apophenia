import helpers

helpers.getStockDatasetsFromQuandl('data/dow_change_days_list.txt')
dataframe = helpers.setup_dataframe()
