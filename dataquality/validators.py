import re
import pandas as pd


def check_missing_values(df: pd.DataFrame):
    """Return count and percentage of missing values per column."""
    total_rows = len(df)
    results = {}
    for col in df.columns:
        missing_count = df[col].isna().sum()
        results[col] = {"missing_count": int(missing_count),
            "missing_pct": round((missing_count / total_rows) * 100, 2) if total_rows else 0.0
        }
    return results


def check_duplicates(df: pd.DataFrame, ignore_columns: list = None) -> dict:
    """
    Return count and row indices of duplicated rows.
    ignore_columns lets you exclude columns like auto-increment IDs
    that would otherwise make every row look 'unique' even when the
    actual data is repeated.
    """
    ignore_columns = ignore_columns or []
    compare_df = df.drop(columns=[c for c in ignore_columns if c in df.columns])

    duplicate_mask = compare_df.duplicated(keep="first")
    return {
        "duplicate_count": int(duplicate_mask.sum()),
        "duplicate_indices": df[duplicate_mask].index.tolist()
    }


def check_range(df: pd.DataFrame, column, min_val=None, max_val=None):
    """Flag values outside an expected numeric range for a column."""
    if column not in df.columns:
        return {"error": f"Column '{column}' not found"}

    series = pd.to_numeric(df[column], errors="coerce")
    invalid_mask = pd.Series(False, index=df.index)

    if min_val is not None:
        invalid_mask |= (series < min_val)
    if max_val is not None:
        invalid_mask |= (series > max_val)

    # Also flag values that couldn't be converted to numeric at all
    non_numeric_mask = series.isna() & df[column].notna()
    invalid_mask |= non_numeric_mask

    invalid_indices = df[invalid_mask].index.tolist()

    return {"column": column, "invalid_count": len(invalid_indices), "invalid_indices": invalid_indices, "expected_range": f"{min_val}–{max_val}"}


def check_regex(df: pd.DataFrame, column, pattern):
    """Flag values in a column that don't match a required regex pattern."""
    if column not in df.columns:
        return {"error": f"Column '{column}' not found"}

    compiled = re.compile(pattern)
    invalid_indices = []

    for idx, value in df[column].items():
        if pd.isna(value):
            continue
        if not compiled.match(str(value)):
            invalid_indices.append(idx)

    return {
        "column": column,
        "invalid_count": len(invalid_indices),
        "invalid_indices": invalid_indices
    }


def check_dtype(df: pd.DataFrame, column, expected_type):
    """Flag values that don't match the expected type (int, float, str)."""
    if column not in df.columns:
        return {"error": f"Column '{column}' not found"}

    invalid_indices = []

    for idx, value in df[column].items():
        if pd.isna(value):
            continue
        try:
            if expected_type == "int":
                int(value)
            elif expected_type == "float":
                float(value)
            elif expected_type == "str":
                str(value)
        except (ValueError, TypeError):
            invalid_indices.append(idx)

    return {
        "column": column,
        "invalid_count": len(invalid_indices),
        "invalid_indices": invalid_indices,
        "expected_type": expected_type
    }