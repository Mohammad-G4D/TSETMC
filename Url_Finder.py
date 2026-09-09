import requests

def Url_Finder(stock):
    """
    Finds the API URL for retrieving historical daily closing price data
    of a given stock symbol from the Tehran Stock Exchange (TSETMC).
    """
    
    # Base URLs for searching instrument code and price history
    api = 'https://cdn.tsetmc.com/api/Instrument/GetInstrumentSearch/' + stock
    based_url = 'https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/'

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Referer": "https://www.tsetmc.com/",
        "Accept": "application/json"
    }

    # Search for the instrument to get its internal code (insCode)
    response = requests.get(api, headers=headers, timeout=20)
    data = response.json()

    # Extract matching instrument codes
    ins_codes = []
    for instrument in data.get('instrumentSearch', []):
        lval_raw = instrument.get('lVal18AFC')
        if lval_raw == stock:
            ins_code = instrument.get('insCode')
            if ins_code:
                ins_codes.append(ins_code)

    # If no matching code is found, return None
    if not ins_codes:
        return None

    ins_codes.sort(reverse=True)
    
    best_ins_code = ins_codes[0]

    return based_url + best_ins_code + '/200000'

