""" Performance metrics """
from typing import List
from sklearn.metrics import confusion_matrix

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