from datetime import timedelta
import jdatetime
import numpy as np
import pandas as pd

from scipy.interpolate import CubicSpline


def Liquidity():
    """
    Reads monthly liquidity data from an Excel file, generates a continuous daily 
    Jalali date range, applies cubic spline interpolation to convert monthly data 
    into daily frequency, shifts the data, saves the result to a CSV file, and 
    returns the daily DataFrame.
    """
    # Read the monthly liquidity data from an Excel file
    df_monthly = pd.read_excel("Raw_Liquidity.xlsx", engine="openpyxl", index_col=0)

    # 1. Generate daily Jalali date range
    min_date_str = str(df_monthly.index[0])
    max_date_str = str(df_monthly.index[-1])

    s_y, s_m, s_d = map(int, min_date_str.split("-"))
    e_y, e_m, e_d = map(int, max_date_str.split("-"))

    jal_start = jdatetime.date(s_y, s_m, s_d)
    jal_end = jdatetime.date(e_y, e_m, e_d)

    full_dates = []
    current = jal_start
    while current <= jal_end:
        full_dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    # 2. Prepare numerical index for non-linear interpolation
    df_daily = df_monthly.reindex(full_dates)
    
    # Convert daily dates to sequential numeric array (Day 0, Day 1, Day 2, ...)
    x_all = np.arange(len(df_daily))
    
    # Identify indices corresponding to available monthly data points (non-NaN)
    valid_mask = ~df_daily["liq"].isna()
    x_known = x_all[valid_mask]

    # 3. Perform cubic spline interpolation for the selected columns
    for col in ["liq", "money"]:
        y_known = df_daily.loc[valid_mask, col].values

        cs = CubicSpline(x_known, y_known, bc_type="natural")
        df_daily[col] = cs(x_all)

    # 4. Shift data backward by 1 day and remove the final row
    df_daily = df_daily.shift(-1)
    df_daily.drop(df_daily.index[-1], axis=0, inplace=True)

    # 5. Save the final processed output to a CSV file
    df_daily.to_csv("Liquidity.csv", sep=",", encoding="utf-8-sig", index=True)

    # Return the resulting daily DataFrame
    return df_daily