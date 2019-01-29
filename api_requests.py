import requests
from datetime import date
from settings import API_GLOBAL_DATA, API_SEARCH, FUNCTION_QUERY

def search_quote(stock):
    search = requests.get(API_SEARCH.format(stock.split(" ")[0])).json()

    if len(search["bestMatches"])==0:
        return None
    else:
        for stock_data in search["bestMatches"]:
            if stock in stock_data["2. name"].lower():
                return stock_data


def get_quote_data(quote):
    data = requests.get(API_GLOBAL_DATA.format(quote)).json()
    
    if "Error Message" in data:
        raise ValueError(data["Error Message"])
    elif "Information" in data:
        raise ValueError(data["Information"])
    elif "Note" in data:
        print(data["Note"])
        return False
    elif "Global Quote" in data:
        return data["Global Quote"]
