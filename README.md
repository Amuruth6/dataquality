# Data Quality & Anomaly Detection Engine

A Python tool that scans CSV/Excel datasets and automatically detects data quality
issues — missing values, duplicate records, invalid formats, out-of-range values,
and statistical anomalies — then produces a quality score and a report (console
and HTML).

## Why I built this
Real-world datasets are messy — missing fields, duplicate entries, malformed
emails, impossible values (like age 150), and outliers that skew analysis. Most
teams catch these manually or too late. This tool automates that check as a
repeatable step before data gets used downstream.

## What it checks
- **Missing values** — count and percentage per column
- **Duplicate rows** — with configurable columns to ignore (e.g. auto-increment
  IDs, which would otherwise make every row look "unique")
- **Range violations** — e.g. age must be 18–100
- **Format violations** — regex-based checks (e.g. valid email format)
- **Type mismatches** — expected int/float/str per column
- **Statistical outliers** — via IQR or Z-score

## Example output

==================================================
![image alt](https://github.com/Amuruth6/dataquality/blob/7407503b4581e49a85dbae6c053dd6200dfb717d/Screenshot%202026-09-06%20195524.png)

## Engineering decisions

**Why IQR over Z-score as the default outlier method:** Z-score assumes data is
roughly normally distributed and is sensitive to the extreme values it's trying
to detect (since they inflate the mean and standard deviation used to calculate
it). IQR is based on quartiles, so it's more robust to skewed, real-world data
like salaries, which is why it's used as the default here. Both methods are
implemented; either can be selected per column in the config.

**A bug I found and fixed:** My first version of duplicate-detection compared
entire rows, including the `id` column. Since IDs are always unique, this meant
identical records (same name, age, email, salary — just a different auto-generated
ID) were never flagged as duplicates. I fixed this by letting duplicate checks
explicitly ignore specified columns (see `check_duplicates(ignore_columns=...)`),
since an ID is metadata about a row, not part of its actual content.

**Validating outlier detection against known values:** I generated a synthetic
5,100-row dataset with 10 deliberately injected extreme salary values, then ran
IQR-based detection and got 47 flagged outliers — not just the 10 I planted. This
confirmed the detection is working on real statistical distribution properties,
not simply matching values I already knew were wrong.

## Tech stack
Python, pandas, NumPy, PyYAML, Click, pytest

## Setup
```bash
pip install -r requirements.txt
python main.py --config config.yaml
```

Edit `config.yaml` to point at your own file and define validation rules per
column:
```yaml
file: sample_data/customers.csv

duplicate_check:
  ignore_columns: ["id"]

rules:
  age:
    type: int
    min: 18
    max: 100
  email:
    type: str
    regex: "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$"
  salary:
    type: float
    outlier_method: iqr
```

## Testing
25 unit tests covering validators, anomaly detection, and scoring — including
edge cases like zero-variance columns, empty dataframes, and ID-column exclusion:
```bash
pytest tests/ -v
```

## Known limitations
- Only supports CSV and Excel input; no database or API ingestion yet
- Outlier detection uses classical statistics (IQR/Z-score), not machine learning
- No REST API or persistent storage — runs as a one-off script per file
- Regex/range/type rules must be manually configured per column; no automatic
  schema inference

## Roadmap (not yet built)
- ML-based anomaly detection (e.g. Isolation Forest) for multivariate anomalies
  that simple per-column statistics can't catch
- REST API to submit files and retrieve reports programmatically
- Persistent storage (SQL database) to track data quality trends over time
- Live dashboard for non-technical users to browse reports
