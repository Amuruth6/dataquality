import pandas as pd
import pytest
from dataquality.validators import (
    check_missing_values,
    check_duplicates,
    check_range,
    check_regex,
    check_dtype,
)


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "id": [1, 2, 3, 4],
        "age": [25, 17, None, 150],
        "email": ["a@x.com", "bad-email", "c@x.com", None],
        "salary": [50000, 52000, 48000, 51000],
    })


# --- check_missing_values ---

def test_missing_values_detects_correct_count(sample_df):
    result = check_missing_values(sample_df)
    assert result["age"]["missing_count"] == 1
    assert result["email"]["missing_count"] == 1
    assert result["id"]["missing_count"] == 0


def test_missing_values_percentage_calculation(sample_df):
    result = check_missing_values(sample_df)
    # 1 missing out of 4 rows = 25%
    assert result["age"]["missing_pct"] == 25.0


def test_missing_values_empty_dataframe():
    df = pd.DataFrame({"col": []})
    result = check_missing_values(df)
    assert result["col"]["missing_count"] == 0
    assert result["col"]["missing_pct"] == 0.0


# --- check_duplicates ---

def test_duplicates_ignores_id_column():
    # Same data, different IDs — should be flagged as duplicate when ignoring 'id'
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["John", "John", "Alice"],
        "age": [28, 28, 30],
    })
    result = check_duplicates(df, ignore_columns=["id"])
    assert result["duplicate_count"] == 1
    assert result["duplicate_indices"] == [1]


def test_duplicates_without_ignoring_id_finds_none():
    # Without ignoring 'id', rows look unique since IDs differ
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["John", "John", "Alice"],
        "age": [28, 28, 30],
    })
    result = check_duplicates(df, ignore_columns=[])
    assert result["duplicate_count"] == 0


def test_duplicates_no_duplicates_present():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    result = check_duplicates(df)
    assert result["duplicate_count"] == 0
    assert result["duplicate_indices"] == []


def test_duplicates_all_rows_identical():
    df = pd.DataFrame({"a": [1, 1, 1], "b": ["x", "x", "x"]})
    result = check_duplicates(df)
    # 3 identical rows -> 2 flagged as duplicates of the first
    assert result["duplicate_count"] == 2


# --- check_range ---

def test_range_flags_below_minimum(sample_df):
    result = check_range(sample_df, "age", min_val=18, max_val=100)
    assert 1 in result["invalid_indices"]  # age 17


def test_range_flags_above_maximum(sample_df):
    result = check_range(sample_df, "age", min_val=18, max_val=100)
    assert 3 in result["invalid_indices"]  # age 150


def test_range_ignores_missing_values(sample_df):
    result = check_range(sample_df, "age", min_val=18, max_val=100)
    # index 2 (None) should NOT be flagged as invalid — it's missing, not out-of-range
    assert 2 not in result["invalid_indices"]


def test_range_missing_column_returns_error(sample_df):
    result = check_range(sample_df, "nonexistent", min_val=0, max_val=10)
    assert "error" in result


# --- check_regex ---

def test_regex_flags_invalid_email_format(sample_df):
    result = check_regex(sample_df, "email", r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    assert 1 in result["invalid_indices"]  # "bad-email"


def test_regex_ignores_missing_values(sample_df):
    result = check_regex(sample_df, "email", r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    # index 3 is None — should be skipped, not flagged
    assert 3 not in result["invalid_indices"]


def test_regex_valid_emails_not_flagged(sample_df):
    result = check_regex(sample_df, "email", r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    assert 0 not in result["invalid_indices"]  # "a@x.com" is valid
    assert 2 not in result["invalid_indices"]  # "c@x.com" is valid


# --- check_dtype ---

def test_dtype_valid_ints_pass():
    df = pd.DataFrame({"col": [1, 2, 3]})
    result = check_dtype(df, "col", "int")
    assert result["invalid_count"] == 0


def test_dtype_invalid_values_flagged():
    df = pd.DataFrame({"col": ["1", "abc", "3"]})
    result = check_dtype(df, "col", "int")
    assert result["invalid_count"] == 1