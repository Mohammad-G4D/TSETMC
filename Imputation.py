import pandas as pd

def Imputation(df):
    """
    Imputes missing values in specified global and local 
    market columns using forward fill from the first valid index.
    """
    df_imputed = df.copy()

    # Define global market columns
    global_market_cols = [
        'Aluminium', 'Brent_Oil', 'USDCNY', 'Coal', 'Cotton', 'DXY',
        'Gold', 'Copper', 'Heating_Oil', 'Steel_HRC', 'Lead', 'Natural_Gas',
        'Sugar', 'Silver', 'Iron_Ore', 'Urea', 'Zinc'
    ]

    # Define local market columns
    local_market_cols = ['USD', 'YTM_average']

    # Combine all columns targeted for forward fill
    cols_to_ffill = global_market_cols + local_market_cols

    # Apply forward fill starting from the first valid index
    for col in cols_to_ffill:
        if col in df_imputed.columns:
            first_idx = df_imputed[col].first_valid_index()
            if first_idx is not None:
                df_imputed.loc[first_idx:, col] = df_imputed.loc[first_idx:, col].ffill()

    return df_imputed