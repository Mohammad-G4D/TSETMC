import jdatetime
import pandas as pd
import yfinance as yf
import warnings

warnings.filterwarnings("ignore")

def Commodities():
    """
    Downloads historical close prices for a predefined list of commodity and financial tickers 
    from Yahoo Finance starting from January 1, 2000, converts the Gregorian dates to the Jalali 
    calendar format, cleans and sorts the data, and saves it to a CSV file named 'Commodities.csv'.
    """
    
    # Helper function to convert Gregorian datetime to Jalali date string
    def get_jalali_date(gregorian_date):
        return jdatetime.date.fromgregorian(date=gregorian_date.date()).strftime('%Y-%m-%d')

    # Dictionary of commodity tickers and their corresponding names
    tickers = {
        'Copper': 'HG=F',
        'Brent_Oil': 'BZ=F',
        'Aluminium': 'ALI=F',
        'Zinc': 'ZN=F',
        'Lead': 'LE=F',
        'Gold': 'GC=F',
        'Silver': 'SI=F',
        'Iron_Ore': 'TIO=F',
        'Natural_Gas': 'NG=F',
        'Steel_HRC': 'HRC=F',
        'DXY': 'DX-Y.NYB',
        'USDCNY': 'CNY=X',
        'Urea': 'UME=F',
        'Sugar': 'SB=F',
        'Heating_Oil': 'HO=F',
        'Cotton': 'CT=F',
        'Coal': 'COAL'
    }

    # Reverse mapping for renaming columns
    ticker_to_name = {v: k for k, v in tickers.items()}
    start_date = "2000-01-01"

    # Download all historical data from Yahoo Finance starting from 2000
    commodities = yf.download(list(tickers.values()), start=start_date, progress=False, auto_adjust=True)

    # Extract 'Close' prices if the dataframe has a MultiIndex structure
    if isinstance(commodities.columns, pd.MultiIndex):
        df = commodities['Close']
    else:
        df = commodities

    # Rename columns to user-friendly names
    df = df.rename(columns=ticker_to_name)
        
    # Convert index to datetime and map it to Jalali calendar format
    df.index = pd.to_datetime(df.index)
    df.index = df.index.map(get_jalali_date)
    df.index.name = 'date'

    # Drop rows where all values are NaN
    df = df.dropna(how='all')

    # Sort data chronologically by date
    df.sort_index(ascending=True, inplace=True)
        
    # Save directly to CSV (overwriting any existing file)
    df.to_csv("Commodities.csv", sep=',', encoding='utf-8-sig')
    return df


Commodities()