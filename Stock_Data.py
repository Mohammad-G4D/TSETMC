import pandas as pd
import jdatetime
import requests

import Url_Finder as ur  # Module to retrieve the data URL for a given stock symbol

def Stock_Data(stock):
    """
    Fetches historical daily data for a specific stock from TSETMC,
    processes and adjusts prices for splits/dividends, and returns a cleaned DataFrame.
    """
    # Get the specific API URL for the stock's historical data
    url = ur.Url_Finder(stock)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Referer": "https://www.tsetmc.com/",
        "Accept": "application/json"
    }

    # Fetch raw JSON data

    response = requests.get(url, headers=headers)
    data = response.json()
    df = pd.DataFrame(data)

    # Flatten nested structure
    dict_column = df.columns[0]
    df = df[dict_column].apply(pd.Series)

    # Select relevant columns
    df = df[['dEven', 'priceYesterday', 'pClosing', 'pDrCotVal', 'qTotCap']].copy()

    # Rename columns for clarity
    df.rename(columns={
        'dEven': 'date',
        'qTotCap': 'vol_rial'
    }, inplace=True)

    # Convert Gregorian date to Jalali and set as index
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    df['date'] = df['date'].map(lambda x: jdatetime.date.fromgregorian(date=x).strftime('%Y-%m-%d'))
    df.set_index('date', inplace=True)

    # Remove rows with missing or zero values
    df.dropna(axis=0, inplace=True)
    df = df[(df != 0).all(axis=1)]

    # Sort by date (earliest first)
    df = df.sort_index(ascending=True)

    # Prepare raw price columns
    df['priceClosing'] = df['pClosing'].copy()
    df['priceFinal'] = df['pDrCotVal'].copy()

    # Calculate daily adjustment ratios
    df['adj_ratio_closing'] = df['pClosing'] / df['priceYesterday']
    df['adj_ratio_final'] = df['pDrCotVal'] / df['priceYesterday']

    # Backward-adjust closing prices for splits and dividends
    cum_ratio = df['adj_ratio_closing'].iloc[1:][::-1].cumprod()[::-1]
    df['priceClosing'] = df['priceClosing'].iloc[-1]
    df.iloc[:-1, df.columns.get_loc('priceClosing')] = (
        df['priceClosing'].iloc[-1] / cum_ratio)

    # Adjust final (trade) prices using the same logic
    df['priceFinal'] = df['adj_ratio_final'] * (df['priceClosing'] / df['adj_ratio_closing'])

    # Drop temporary and raw columns
    df.drop(columns=['priceYesterday', 'pClosing', 'pDrCotVal',
                     'adj_ratio_final', 'adj_ratio_closing'], inplace=True)

    file_name = stock + '.csv'
    df.to_csv(file_name, index=True, sep=',', encoding='utf-8-sig', header=True)

    return df

