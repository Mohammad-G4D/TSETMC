import warnings
import Feature_Engineering as fte
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller

warnings.filterwarnings('ignore')


def Stationarity_Filter(df):
  """
  Filters out non-stationary numeric features using the Augmented Dickey-Fuller (ADF) test.
  """

  # Set significance level for ADF test
  p_value_threshold = 0.05

  # Define protected columns that should not be dropped
  protected_cols = set(
      fte.calendar_cols + fte.evaluation_cols + fte.other_important_cols
  )
  df_clean = df.copy()

  # Align valid indices using the shifted target column
  y = df_clean[fte.target_col].shift(-1).dropna()
  valid_idx = y.index

  # Identify numeric columns excluding protected ones
  numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
  candidate_cols = [col for col in numeric_cols if col not in protected_cols]

  non_stationary_cols = []
  stationary_count = 0

  # Check stationarity for each candidate column
  for col in candidate_cols:
    series = df_clean.loc[valid_idx, col].dropna()

    # Skip if series is too short, constant, or has zero variance
    if len(series) < 30 or series.nunique() <= 1 or series.std() == 0:
      non_stationary_cols.append(col)
      continue

    try:
      # Perform Augmented Dickey-Fuller test
      p_val = adfuller(series.values, autolag='AIC')[1]

      # Check p-value against threshold
      if p_val >= p_value_threshold:
        non_stationary_cols.append(col)
      else:
        stationary_count += 1
    except Exception:
      non_stationary_cols.append(col)

  # Drop non-stationary columns from the DataFrame
  df_clean.drop(columns=non_stationary_cols, inplace=True)

  return df_clean