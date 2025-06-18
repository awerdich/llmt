""" Performance metrics """
from typing import List
import pandas as pd
from sklearn.metrics import confusion_matrix
import logging

logger = logging.getLogger(__name__)

def binary_performance(y_true: List[int], y_pred: List[int], decimals: int=4) -> dict:
    tn, fp, fn, tp = confusion_matrix(y_true=y_true, y_pred=y_pred).ravel()
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    performance_dict = {'p': y_true.count(1), # Number of positive samples in true data
                        'n': y_true.count(0), # Number of negative samples in true data
                        'tp': int(tp),
                        'tn': int(tn),
                        'fp': int(fp),
                        'fn': int(fn),
                        'recall': round(float(recall), decimals), # Sensitivity true positive rate
                        'precision': round(float(precision), decimals), # Fraction of correctly identified positive samples
                        'min_precision': round(float((tp + fn) / len(y_true)), decimals), # Assume we return all predictions as positive
                        'specificity': round(float(tn / (tn + fp)), decimals), # True negative rate
                        'f_score': round(float(2 * (precision * recall) / (precision + recall)), decimals)}
    return performance_dict

class Performance:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def combine_binary_columns(self, input_col_list: list,
                               id_col: str='id',
                               output_col_name: str=None):
        if output_col_name is None:
            output_col_name = '_'.join(input_col_list)
        df = self.data[[id_col, *input_col_list]]
        # Remove all rows with values different from 0 or 1
        for col in input_col_list:
            df = df.loc[df[col].isin([0, 1])]
            df[col] = (df[col].astype(int))
        if len(df) < len(self.data): logger.warning(f'{len(self.data) - len(df)} rows removed from data!')
        # Add the binary columns
        df[output_col_name] = df[input_col_list].sum(axis=1)
        df[output_col_name] = df[output_col_name].apply(lambda val: 1 if val == len(input_col_list) else 0)
        return df

    def binary_performance(self, true_col: str, pred_col: str) -> dict:
        df = self.data[[true_col, pred_col]].\
            dropna(axis=0, how='any')
        # Set the types for the predictions
        df = df.astype({true_col: int, pred_col: int})
        df = df.loc[df[true_col].isin([0, 1])]
        df = df.loc[df[pred_col].isin([0, 1])]
        y_true = df[true_col].tolist()
        y_red = df[pred_col].tolist()
        performance_dict = binary_performance(y_true=y_true, y_pred=y_red)
        return performance_dict
