import pandas as pd
import numpy as np
import optuna

import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.multioutput import MultiOutputRegressor


def XGB_Params(X_tr, Y_tr, n_trials=15):
    """
    Optimizes XGBoost hyperparameters for multi-output time-series forecasting using Optuna 
    and TimeSeriesSplit cross-validation to prevent data leakage.
    """
    
    def objective(trial):

        # Suggest a set of hyperparameters for the current Optuna trial
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 300),
            'max_depth': trial.suggest_int('max_depth', 4, 8),
            'learning_rate': trial.suggest_float('learning_rate', 0.02, 0.15, log=True),
            'subsample': trial.suggest_float('subsample', 0.6, 0.9),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 0.9),
            'reg_alpha': trial.suggest_float('reg_alpha', 1e-3, 1.0, log=True),
            'reg_lambda': trial.suggest_float('reg_lambda', 1e-3, 1.0, log=True),
            'gamma': trial.suggest_float('gamma', 0.0, 1.0),
            'objective': 'reg:absoluteerror',
            'tree_method': 'hist',
            'device': 'cuda'
        }
        
        # Initialize the base XGBoost model and wrap it for multi-output regression
        base_xgb = xgb.XGBRegressor(**params)
        model = MultiOutputRegressor(base_xgb)
        
        tscv = TimeSeriesSplit(n_splits=3)
        scores = []
        
        # Iterate through time-series cross-validation folds
        for train_idx, val_idx in tscv.split(X_tr):
            X_cv_train, X_cv_val = X_tr[train_idx], X_tr[val_idx]
            Y_cv_train, Y_cv_val = Y_tr[train_idx], Y_tr[val_idx]
            
            model.fit(X_cv_train, Y_cv_train)
            preds = model.predict(X_cv_val)
            
            # Calculate Mean Absolute Error (MAE) for the current fold
            mae = np.mean(np.abs(Y_cv_val - preds))
            scores.append(mae)
            
        # Return the average MAE across all time-series folds
        return np.mean(scores)

    # Create an Optuna study to minimize the validation error
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=n_trials)
    
    # Extract the best hyperparameters and ensure critical fixed configurations are set
    best_params = study.best_params
    best_params['objective'] = 'reg:absoluteerror'
    best_params['tree_method'] = 'hist'
    best_params['device'] = 'cuda'
    
    return best_params