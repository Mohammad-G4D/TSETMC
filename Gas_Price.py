from datetime import timedelta
import jdatetime
import numpy as np
import pandas as pd

from scipy.interpolate import CubicSpline

def Gas_Price():
    """
    Reads yearly gas price data from an Excel file, generates a continuous daily 
    Jalali date range, applies cubic spline interpolation to convert yearly data 
    into daily frequency, saves the result to a CSV file, and 
    returns the daily DataFrame.
    """

    df_yearly = pd.read_excel("Raw_Gas_Price.xlsx", engine="openpyxl")

    # 1. Generate daily Jalali date range (Exactly like monthly code)
    min_year = int(df_yearly["date"].iloc[0])
    max_year = int(df_yearly["date"].iloc[-1])

    jal_start = jdatetime.date(min_year, 1, 1)
    jal_end = jdatetime.date(max_year, 12, 29)

    full_dates = []
    current = jal_start
    while current <= jal_end:
        full_dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    # Create empty daily DataFrame indexed by daily dates
    df_daily = pd.DataFrame(index=full_dates, columns=["Gas_Price"])
    df_daily.index.name = "date"

    # 2. Map yearly values to the last day of each year (YYYY-12-29)
    for _, row in df_yearly.iterrows():
        yr = int(row["date"])
        val = row["Gas_Price"]
        target_date = f"{yr:04d}-12-29"

        if target_date in df_daily.index:
            df_daily.loc[target_date, "Gas_Price"] = val

    df_daily["Gas_Price"] = pd.to_numeric(
        df_daily["Gas_Price"], errors="coerce"
    )

    # 3. Prepare numerical index for non-linear interpolation
    x_all = np.arange(len(df_daily))

    # Identify indices corresponding to available yearly data points (non-NaN)
    valid_mask = ~df_daily["Gas_Price"].isna()
    x_known = x_all[valid_mask]
    y_known = df_daily.loc[valid_mask, "Gas_Price"].values

    # 4. Perform Cubic Spline Interpolation
    cs = CubicSpline(x_known, y_known, bc_type="natural")
    df_daily["Gas_Price"] = cs(x_all)

    # 5. Save output to CSV
    df_daily.to_csv("Gas_Price.csv", sep=",", encoding="utf-8-sig", index=True)

    return df_daily
