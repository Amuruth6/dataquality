import pandas as pd
import pytest
from dataquality.anomaly import detect_outliers_iqr, detect_outliers_zscore


def test_iqr_detects_clear_outlier():
    df = pd.DataFrame({"salary": [50000, 52000, 48000, 51000, 49000, 950000]})
    result = detect_outliers_iqr(df, "salary")
    assert 5 in result["outlier_indices"]  # index of 950000
    assert result["outlier_count"] == 1


def test_iqr_no_outliers_in_uniform_data():
    df = pd.DataFrame({"col": [10, 11, 12, 13, 14, 15]})
    result = detect_outliers_iqr(df, "col")
    assert result["outlier_count"] == 0


def test_iqr_handles_insufficient_data():
    df = pd.DataFrame({"col": [10, 20]})  # fewer than 4 points
    result = detect_outliers_iqr(df, "col")
    assert result["outlier_count"] == 0
    assert "note" in result


def test_iqr_missing_column_returns_error():
    df = pd.DataFrame({"col": [1, 2, 3, 4]})
    result = detect_outliers_iqr(df, "nonexistent")
    assert "error" in result


def test_zscore_detects_clear_outlier():
    df = pd.DataFrame({"salary": [50000, 51000, 49000, 50500, 49500, 200000]})
    result = detect_outliers_zscore(df, "salary", threshold=2.0)
    assert result["outlier_count"] >= 1


def test_zscore_handles_zero_variance():
    df = pd.DataFrame({"col": [5, 5, 5, 5, 5]})
    result = detect_outliers_zscore(df, "col")
    assert result["outlier_count"] == 0
    assert "note" in result