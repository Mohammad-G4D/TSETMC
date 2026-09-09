import pandas as pd
import requests
import jdatetime
import time
import random


def USD():
        
    """Fetch recent free market USD rates from TGJU API using pagination."""
    url_based = "https://api.tgju.org/v1/market/indicator/summary-table-data/price_dollar_rl?lang=fa&order_dir=asc&draw=1&columns%5B0%5D%5Bdata%5D=0&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=1&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=2&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=3&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=4&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=5&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=6&columns%5B6%5D%5Bname%5D=&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B7%5D%5Bdata%5D=7&columns%5B7%5D%5Bname%5D=&columns%5B7%5D%5Bsearchable%5D=true&columns%5B7%5D%5Borderable%5D=true&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D%5Bsearch%5D%5Bregex%5D=false&start=0&length=30&search=&order_col=&order_dir=&from=&to=&convert_to_ad=1"

    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Referer": "https://www.tgju.org/profile/price_dollar_rl/history",
            "Accept": "application/json"
        }

    all_data = []
    start = 0
    length = 100

    # Paginate through all available data
    while True:
        url = f"{url_based}&start={start}&length={length}"
        response = requests.get(url, headers=headers)
        data = response.json()
        rows = data.get("data", [])

        for row in rows:
            # Extract closing price and clean commas
            price_c = row[3].replace(",", "")
            dolar_close = float(price_c)
            greg_date = row[6].strip()

            all_data.append({
                "date": greg_date,
                "USD": dolar_close
                })

        # Break if last page
        if len(rows) < length:
            break

        start += 100
        # Random delay to avoid rate limiting
        time.sleep(random.uniform(0.3, 0.7))

    # Create DataFrame and convert Gregorian dates to Jalali
    USD = pd.DataFrame(all_data)
    USD['date'] = pd.to_datetime(USD['date'], format="%Y/%m/%d")
    USD['date'] = USD['date'].map(
        lambda x: jdatetime.date.fromgregorian(date=x).strftime('%Y-%m-%d'))
    USD.set_index('date', inplace=True)

    USD.sort_index(ascending=True, inplace=True)
    USD.to_csv('USD.csv', sep=',', encoding='utf-8-sig', index=True, index_label='date')

    return USD
