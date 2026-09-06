import pandas as pd
import numpy as np

np.random.seed(42)  # reproducible results

N_ROWS = 5000

# --- Generate mostly clean data ---
ids = np.arange(1, N_ROWS + 1)
ages = np.random.randint(18, 65, size=N_ROWS)
salaries = np.random.normal(loc=55000, scale=12000, size=N_ROWS).round(2)
names = [f"Person_{i}" for i in ids]
emails = [f"person{i}@example.com" for i in ids]

df = pd.DataFrame({
    "id": ids,
    "name": names,
    "age": ages,
    "email": emails,
    "salary": salaries,
})

# --- Inject realistic problems ---

# 1. Missing values (~3% of age and email)
missing_age_idx = np.random.choice(df.index, size=int(N_ROWS * 0.03), replace=False)
df.loc[missing_age_idx, "age"] = None

missing_email_idx = np.random.choice(df.index, size=int(N_ROWS * 0.02), replace=False)
df.loc[missing_email_idx, "email"] = None

# 2. Duplicate rows (~2% — copy some existing rows, keep their same data but new IDs would defeat the purpose, so duplicate with SAME id-independent content)
dup_source_idx = np.random.choice(df.index, size=int(N_ROWS * 0.02), replace=False)
duplicated_rows = df.loc[dup_source_idx].copy()
duplicated_rows["id"] = range(N_ROWS + 1, N_ROWS + 1 + len(duplicated_rows))  # new IDs, same content
df = pd.concat([df, duplicated_rows], ignore_index=True)

# 3. Invalid ages (some below 18, some impossible)
invalid_age_idx = np.random.choice(df.index, size=30, replace=False)
df.loc[invalid_age_idx[:15], "age"] = np.random.randint(1, 17, size=15)
df.loc[invalid_age_idx[15:], "age"] = np.random.randint(101, 200, size=15)

# 4. Invalid emails (malformed)
invalid_email_idx = np.random.choice(df.index, size=25, replace=False)
df.loc[invalid_email_idx, "email"] = "not-a-valid-email"

# 5. Salary outliers (unrealistic extreme values)
outlier_idx = np.random.choice(df.index, size=10, replace=False)
df.loc[outlier_idx, "salary"] = np.random.choice([5000, 2000000, 3500000], size=10)

# Shuffle rows so injected issues aren't clustered at the end
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

df.to_csv("sample_data/customers_large.csv", index=False)
print(f"Generated {len(df)} rows -> sample_data/customers_large.csv")