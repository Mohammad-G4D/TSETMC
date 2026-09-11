import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
from sklearn.multioutput import MultiOutputRegressor

import Feature_Engineering as fte
import XGBoost_Dataset as xgbd
import Hyperparameter_Tuning as hyp
import Adjust_Prices as adjp
import Plot


def XGBoost(df):
    """
    Executes a walk-forward validation and multi-step forecasting pipeline 
    using XGBoost and Optuna for hyperparameter optimization.
    """
    
    # Define time-series sequence and prediction parameters
    seq_len = 60          # Number of historical time steps to look back
    step_size = 20        # Step size for advancing the walk-forward window
    pred_horizon = 7      # Number of future steps to forecast

    # Extract valid feature columns by excluding calendar and evaluation columns
    feature_cols = [c for c in df.columns if c not in (fte.calendar_cols + fte.evaluation_cols)]

    # Reset dataframe index and ensure date column is in string format for filtering
    df = df.reset_index()
    df['date'] = df['date'].astype(str)

    # Determine the starting index for backtesting/walk-forward evaluation
    start_date = '1401-01-01'
    indices = df[df['date'] >= start_date].index.tolist()
    start_idx = indices[0]
     
    # Enable interactive mode for real-time plot updates
    plt.ion()

    # Iterate through the dataset using a walk-forward approach
    for n_idx in range(start_idx, len(df)-pred_horizon, step_size):

        # Get the current base date for the forecast window
        current_date = df.loc[n_idx + 1, 'date']
        
        # Slice the historical training data up to the current index
        df_train = df.iloc[:n_idx + 1].copy()

        # Scale the training features using StandardScaler
        scaler = StandardScaler()
        df_train[feature_cols] = scaler.fit_transform(df_train[feature_cols])
        
        # Create supervised learning dataset structures (X and Y)
        X_train, Y_train = xgbd.Create_XGBoost_Dataset(df_train)

        # Optimize hyperparameters, initialize model, and fit on training data
        best_params = hyp.XGB_Params(X_train, Y_train)
        base_xgb = xgb.XGBRegressor(**best_params)
        model = MultiOutputRegressor(base_xgb)
        model.fit(X_train, Y_train)

        # Prepare the test feature vector combining past features and future calendar data
        recent_window_flattened = df_train[feature_cols].iloc[-seq_len:].values.flatten()
        future_calendar_window = df[fte.calendar_cols].iloc[n_idx + 1 : n_idx + 1 + pred_horizon].values
        X_test = np.hstack([recent_window_flattened, future_calendar_window.flatten()]).reshape(1, -1)

        # Generate multi-step return predictions and adjust prices accordingly
        predicted_returns = model.predict(X_test)[0]
        pred_prices = adjp.Adjust_Prices(df, df_train, predicted_returns, seq_len, n_idx)

        # Extract actual closing prices and dates for the evaluation horizon
        actual_prices = df.loc[n_idx : n_idx + pred_horizon, 'priceClosing'].values.tolist()
        dates_8_days = df.loc[n_idx : n_idx + pred_horizon, 'date'].tolist()

        # Plot the walk-forward prediction results against actual values
        Plot.Walk_Forward_Plot(dates_8_days, actual_prices, pred_prices, current_date)

    # Disable interactive plotting mode once the loop finishes
    plt.ioff()