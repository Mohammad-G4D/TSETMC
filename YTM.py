import pandas as pd
import requests
import jdatetime
import time
import random
from io import StringIO

import Url_Finder as ur


def Get_YTMs():
    """
    Fetch the list of currently active bonds and their basic details 
    from the official Iran Fara Bourse (IFB) website.

    Returns:
        pd.DataFrame: A DataFrame containing active bond symbols and related details.
    """
    url = 'https://www.ifb.ir/ytm.aspx'

    # Set headers to mimic a real browser request and avoid blocking
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }
    
    # Request the webpage and enforce UTF-8 encoding
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'

    # Parse all HTML tables from the response and select the bonds table
    dfs = pd.read_html(StringIO(response.text))
    df_ytm = dfs[1]

    # Clean column names and standardize the symbol column header
    df_ytm.columns = df_ytm.columns.str.strip()
    df_ytm.rename(columns={'نام نماد': 'نماد'}, inplace=True)

    # Reset index for clean sequential ordering
    df_ytm.reset_index(drop=True, inplace=True)

    return df_ytm


def YTM(url, ytm, application_date):
    """
    Fetch historical price data for a specific bond, compute its remaining lifetime 
    using Jalali dates, and calculate its historical YTM series.
    """

    # Configure headers to interact with the TSETMC API
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Referer": "https://www.tsetmc.com/",
        "Accept": "application/json"
    }

    # Fetch historical data payload from the API endpoint
    response = requests.get(url, headers=headers, timeout=20)
    data = response.json()
    df_ytm = pd.DataFrame(data)

    # Flatten the nested JSON structure returned by the API
    dict_column = df_ytm.columns[0]
    df_ytm = df_ytm[dict_column].apply(pd.Series)

    # Filter and rename essential columns (Date, Closing Price, Volume)
    df_ytm = df_ytm[['dEven', 'pDrCotVal', 'qTotTran5J']]
    df_ytm.rename(columns={
        'dEven': 'date',
        'pDrCotVal': 'priceClosing',
        'qTotTran5J': 'volume'
    }, inplace=True)

    # Convert TSETMC integer date format (e.g., 20231012) to Gregorian datetime,
    # then map it to the Jalali calendar equivalent
    df_ytm['date'] = pd.to_datetime(df_ytm['date'], format='%Y%m%d')
    df_ytm['jalali_date'] = df_ytm['date'].map(
        lambda x: jdatetime.date.fromgregorian(date=x.date())
    )

    # Parse the reference evaluation date as a Jalali date object
    jalali_apply_date = jdatetime.datetime.strptime(application_date, "%Y-%m-%d").date()

    # Calculate remaining days to maturity based on Jalali calendar differences
    df_ytm['t_remained'] = df_ytm['jalali_date'].map(
        lambda x: (jalali_apply_date - x).days
    )

    # Filter out short-term bonds; keep only records with more than 90 days remaining
    df_ytm = df_ytm[df_ytm['t_remained'] > 90]

    # Calculate Yield to Maturity (YTM) using the standard annualized formula
    df_ytm[ytm] = 100 * (((1000000 / df_ytm['priceClosing']) ** (365 / df_ytm['t_remained'])) - 1)

    # Data cleansing: drop missing values and rows containing zero values to prevent math errors
    df_ytm.dropna(axis=0, inplace=True)
    df_ytm = df_ytm[(df_ytm != 0).all(axis=1)]

    # Format Jalali date back to standard string format and assign it as the DataFrame index
    df_ytm['date'] = df_ytm['jalali_date'].map(lambda x: x.strftime('%Y-%m-%d'))
    df_ytm.drop(columns=['jalali_date', 'priceClosing', 't_remained', 'volume'], inplace=True)
    df_ytm.set_index('date', inplace=True)

    return df_ytm


def All_YTMs(df):
    """
    Iterate through all active bonds in the given DataFrame, retrieve their 
    respective history URLs, compute individual YTM series, and merge them together.
    """

    Y = []

    # Loop through each bond in the registry
    for i in range(len(df)):
        # Retrieve the specific data URL for the current bond symbol
        url_YTD = ur.Url_Finder(df.loc[i, 'نماد'])
        
        # Calculate historical YTM series for the current bond
        Yi = YTM(url_YTD, df.loc[i, 'نماد'], df.loc[i, 'تاریخ سررسید'])
        Y.append(Yi)

        # Introduce a randomized sleep delay to prevent rate-limiting or server blocking
        time.sleep(random.uniform(1.5, 3.0))

    # Concatenate all individual bond YTM series into a single wide DataFrame
    YTMs = pd.concat(Y, axis=1, join='outer')
    return YTMs


def YTM_AVG():
    """
    Main function. Fetches active bonds, calculates individual 
    YTM time series, computes the daily market-wide average YTM value, 
    exports the final dataset to a CSV file, and returns the result.
    """

    # Step 1: Fetch active bonds list
    ytm = Get_YTMs()
    
    # Step 2: Compute historical YTM time series for all retrieved bonds
    df = All_YTMs(ytm)

    # Sort chronological records in ascending order
    df.sort_index(ascending=True, inplace=True)
    df = df.copy()

    # Calculate the cross-sectional average YTM across all available bonds for each day
    df['YTM_average'] = df.mean(axis=1)
    df = df[['YTM_average']]

    # Export the resulting average series to a CSV file with proper encoding
    df.to_csv('YTM.csv', index=True, sep=",", encoding="utf-8-sig")

    return df
