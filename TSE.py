import pandas as pd

from Create_Dataset import Create_Dataset
from XGBoost import XGBoost


if __name__ == "__main__":
    # Load and prepare the dataset by calling the dataset creation module
    data = Create_Dataset()

    # Check if the dataset contains enough rows to perform meaningful time-series modeling
    if len(data) > 200:
        # Run the XGBoost walk-forward forecasting pipeline if sufficient data is available
        XGBoost(data)
    else:
        # Display a warning message if the sample size is too small
        print('تعداد داده ناکافی است.\n لطفاً نماد دیگری را انتخاب کنید.\n')

        




