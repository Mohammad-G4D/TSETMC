import pandas as pd

import Stocks_List
import Stock_Data as stc
import Liquidity as lqd
import Gas_Price as gs
import USD
import YTM
import Commodities as cmd
import Calendar_Features as cal
import Imputation
import Text_Editor as txt

import Feature_Engineering as fte
import Stationarity_Filter as stf


def Create_Dataset():
    """
    This function gets a stock symbol from the user, collects and merges stock data 
    with economic indicators, processes missing values, engineers features, 
    filters for stationarity, and exports the final dataset to a CSV file.
    """
    
    # Loop until a valid stock symbol is entered by the user

    while True:
        stock = input('لطفا نام سهام مورد نظر خود را وارد نمایید:\n').strip()
        stock = txt.Normalize_Persian(stock)

        if stock in Stocks_List.stocks.keys():
            stock_data = stc.Stock_Data(stock)
            div = Stocks_List.stocks[stock]
            break
        else:
            print("نماد مورد نظر یافت نشد.\n لطفاً نماد سهام را به درستی وارد نمایید.")

    # Initialize calendar features and market data indicators
    calendar_features = cal.Calendar_Features(div)
    liquidity = lqd.Liquidity()
    gas = gs.Gas_Price()

    # Load YTM data (try fetching live, fallback to local CSV if it fails)
    try:
        ytm = YTM.YTM_AVG()
    except Exception as e:
        ytm = pd.read_csv('YTM.csv', sep=',', index_col=0, encoding='utf-8-sig')

    # Load USD exchange rate data with local CSV fallback
    try:
        usd = USD.USD()
    except Exception as e:
        usd = pd.read_csv('USD.csv', sep=',', index_col=0, encoding='utf-8-sig')

    # Load commodities data with local CSV fallback
    try:
        commodities = cmd.Commodities()
    except Exception as e:
        commodities = pd.read_csv('Commodities.csv', sep=',', index_col=0, encoding='utf-8-sig')

    # Group all dataframes into a single list
    dfs = [stock_data, calendar_features, commodities, ytm, usd, liquidity, gas]

    # Standardize date indices to string and remove whitespace
    for df in dfs:
        df.index = df.index.astype(str).str.strip()

    # Merge all datasets on date index (outer join to keep maximum coverage)
    data = pd.concat(dfs, axis=1, join='outer')

    # Apply data imputation, feature engineering, and stationarity filtering
    imputed_data = Imputation.Imputation(data)
    featured_data = fte.Feature_Engineering(imputed_data)
    non_stationary_data = stf.Stationarity_Filter(featured_data)

    # Export the processed dataset to a CSV file
    filename = f'{stock}.csv'
    non_stationary_data.to_csv(filename, index=True, sep=",", encoding="utf-8-sig", header=True)

    return non_stationary_data