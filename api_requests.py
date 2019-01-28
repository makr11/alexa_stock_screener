import requests
from datetime import date
from stocks import stocks
from settings import API_URL, FUNCTION_QUERY

def get_api_data(quote, date_range):
    """request to API with error check
    Error message if any of query params are invaild
    Note if API call limit is reached"""
    print(API_URL.format(date_range, quote))
    data = requests.get(API_URL.format(date_range, quote)).json()

    if "Error Message" in data:
        raise ValueError(data["Error Message"])
    elif "Information" in data:
        raise ValueError(data["Information"])
    elif "Note" in data:
        print(data["Note"])
        return False
    for i in data:
        if "Time Series" in i:
            return data[i]

def get_price(stock):
    quote = stocks[stock]
    data = get_api_data(quote, "TIME_SERIES_DAILY")
    price = round(float(data[next(iter(data))]['4. close']), 2)
    return f"{price}$"

