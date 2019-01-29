# api defaults
ADDRESS = "https://www.alphavantage.co/query?"
API_KEY = "KOSKZLNCLMKK88OT"
API_TRADING_DATA = ADDRESS + "&function={}&symbol={}&interval=5min&apikey=" + API_KEY
API_SEARCH = ADDRESS + "&function=SYMBOL_SEARCH&keywords={}&apikey=" + API_KEY
API_GLOBAL_DATA = ADDRESS + "&function=GLOBAL_QUOTE&symbol={}&apikey=" + API_KEY
FUNCTION_QUERY = "TIME_SERIES_"
DATE_RANGE = ("INTRADAY", "DAILY", "WEEKLY", "MONTHLY")