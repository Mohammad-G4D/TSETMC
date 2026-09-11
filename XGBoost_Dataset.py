import numpy as np
import pandas as pd

import Feature_Engineering as fte


def Create_XGBoost_Dataset(df):
    """
    Transforms time-series data into a supervised learning format suitable for XGBoost,
    allowing multi-step forecasting based on past features and future calendar data.
    """

    # Define column groups and sequence/prediction lengths
    calendar_cols = fte.calendar_cols
    feature_cols = [c for c in df.columns if c not in (fte.calendar_cols + fte.evaluation_cols)]
    seq_len = 60   # Number of historical time steps to look back
    pred_len = 7   # Number of future steps to forecast
    
    # Extract raw data arrays from the dataframe for faster processing
    raw_features = df[feature_cols].values
    raw_calendar = df[calendar_cols].values
    raw_log_returns = df[fte.target_col].values
    
    # Initialize lists to store features and targets for each window
    X_list, Y_list = [], []
    
    # Slide a window across the dataset to create historical-future pairs
    for i in range(0, len(df) - seq_len - pred_len + 1):
        
        # Extract the historical feature window and the future target window
        x_past = raw_features[i : i + seq_len].copy()
        y_window = raw_log_returns[i + seq_len : i + seq_len + pred_len].copy()
        
        # Flatten the historical feature window into a 1D array
        x_past_flat = x_past.flatten()
        
        # Extract calendar features corresponding to the prediction horizon
        calendar_future = raw_calendar[i + seq_len : i + seq_len + pred_len].copy()
        
        # Combine flattened historical features with future calendar features
        x_combined = np.hstack([x_past_flat, calendar_future.flatten()])
        
        # Append the combined features and target window to their respective lists
        X_list.append(x_combined)
        Y_list.append(y_window)
        
    # Convert lists to NumPy arrays and return
    return np.array(X_list), np.array(Y_list)