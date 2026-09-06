import pandas as pd
from pathlib import Path


def load_data(filepath: str) -> pd.DataFrame:
    """Load a CSV or Excel file into a pandas DataFrame."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    elif suffix in (".xlsx", ".xls"):
        return pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Supported: .csv, .xlsx, .xls")