""" Performance metrics """
from typing import List
import copy
import pandas as pd
from pandas.core.frame import DataFrame
from sklearn.metrics import confusion_matrix
import logging

logger = logging.getLogger(__name__)

def binary_performance(y_true: List[int], y_pred: List[int], decimals: int=4) -> dict:
    tn, fp, fn, tp = confusion_matrix(y_true=y_true, y_pred=y_pred).ravel()
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    if (precision + recall) > 0:
        f_score = round(float(2 * (precision * recall) / (precision + recall)), decimals)
    else:
        f_score = 0
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
                        'f_score': f_score}
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
        # if len(df) < len(self.data): logger.warning(f'{len(self.data) - len(df)} rows removed from data!')
        # Add the binary columns
        df[output_col_name] = df[input_col_list].sum(axis=1)
        df[output_col_name] = df[output_col_name].apply(lambda val: 1 if val == len(input_col_list) else 0)
        return df

    def combine_columns(self, true_col_list: list, pred_col_list: list) -> DataFrame:
        """ Combine binary columns like [true_mh, true_ip] """
        output = copy.deepcopy(self.data)
        success = False
        if len(true_col_list) > 0 and set(true_col_list).issubset(self.data.columns):
            true_combined = self.combine_binary_columns(input_col_list=true_col_list). \
                drop(true_col_list, axis=1)
            output = output.merge(true_combined, on='id', how='left')
            success = True
        if len(pred_col_list) > 0 and set(pred_col_list).issubset(self.data.columns):
            pred_combined = self.combine_binary_columns(input_col_list=pred_col_list). \
                drop(pred_col_list, axis=1)
            output = output.merge(pred_combined, on='id', how='left')
            success = True
        if not success:
            raise ValueError('No valid columns found for combining!')
        return output

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
