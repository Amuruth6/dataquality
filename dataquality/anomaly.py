import pandas as pd
import numpy as np


def detect_outliers_iqr(df: pd.DataFrame, column, multiplier: float = 1.5):
    """
    Detect outliers using the IQR (Interquartile Range) method.
    A value is an outlier if it falls below Q1 - multiplier*IQR
    or above Q3 + multiplier*IQR. Chosen over Z-score because it
    doesn't assume a normal distribution, which is safer for
    real-world skewed data like salaries.
    """
    if column not in df.columns:
        return {"error": f"Column '{column}' not found"}

    series = pd.to_numeric(df[column], errors="coerce").dropna()
    if len(series) < 4:
        return {"column": column, "outlier_count": 0, "outlier_indices": [], "note": "Not enough data points"}

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr

    outlier_mask = (series < lower_bound) | (series > upper_bound)
    outlier_indices = series[outlier_mask].index.tolist()

    return {
        "column": column,
        "method": "IQR",
        "lower_bound": round(lower_bound, 2),
        "upper_bound": round(upper_bound, 2),
        "outlier_count": len(outlier_indices),
        "outlier_indices": outlier_indices
    }


def detect_outliers_zscore(df: pd.DataFrame, column: str, threshold: float = 3.0) -> dict:
    """
    Detect outliers using Z-score: how many standard deviations a value
    is from the mean. Best suited for roughly normally-distributed data.
    """
    if column not in df.columns:
        return {"error": f"Column '{column}' not found"}

    series = pd.to_numeric(df[column], errors="coerce").dropna()
    if len(series) < 4 or series.std() == 0:
        return {"column": column, "outlier_count": 0, "outlier_indices": [], "note": "Not enough variance in data"}

    mean = series.mean()
    std = series.std()
    z_scores = (series - mean).abs() / std

    outlier_mask = z_scores > threshold
    outlier_indices = series[outlier_mask].index.tolist()

    return {
        "column": column,
        "method": "Z-score",
        "mean": round(mean, 2),
        "std_dev": round(std, 2),
        "outlier_count": len(outlier_indices),
        "outlier_indices": outlier_indices
    }