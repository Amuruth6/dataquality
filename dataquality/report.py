def print_console_report(filepath: str, df, missing_results: dict, duplicate_results: dict,
                          rule_results: list, outlier_results: list, score_result: dict):
    total_rows = len(df)
    total_cols = len(df.columns)

    print("=" * 50)
    print("DATA QUALITY REPORT")
    print("=" * 50)
    print(f"File:                 {filepath}")
    print(f"Rows:                 {total_rows:,}")
    print(f"Columns:              {total_cols}")
    print()

    total_missing = sum(v["missing_count"] for v in missing_results.values())
    total_cells = total_rows * total_cols
    missing_pct = round((total_missing / total_cells) * 100, 2) if total_cells else 0

    print(f"Missing Values:       {missing_pct}% ({total_missing} cells)")
    print(f"Duplicate Rows:       {duplicate_results['duplicate_count']}")

    for result in rule_results:
        if "error" in result:
            continue
        label = result["column"]
        print(f"Invalid '{label}':".ljust(22) + f"{result['invalid_count']}")

    for result in outlier_results:
        if "error" in result or "note" in result:
            continue
        print(f"Outliers in '{result['column']}':".ljust(22) + f"{result['outlier_count']} ({result['method']})")

    print()
    print(f"Overall Quality Score: {score_result['score']} / 100")
    print()
    print("Score breakdown (penalty points deducted):")
    for k, v in score_result["breakdown"].items():
        print(f"  {k}: -{v}")

    print()
    if missing_pct > 0:
        print("Columns with missing data:")
        for col, v in missing_results.items():
            if v["missing_count"] > 0:
                print(f"  {col}: {v['missing_count']} missing ({v['missing_pct']}%)")

    print()
    for result in rule_results:
        if "error" in result or result["invalid_count"] == 0:
            continue
        print(f"Column: {result['column']}")
        if "expected_range" in result:
            print(f"  Expected range: {result['expected_range']}")
        sample_indices = result["invalid_indices"][:5]
        print(f"  {result['invalid_count']} invalid values (rows: {sample_indices}{'...' if len(result['invalid_indices']) > 5 else ''})")
        print()

    for result in outlier_results:
        if "error" in result or "note" in result or result["outlier_count"] == 0:
            continue
        print(f"Column: {result['column']} (outliers, {result['method']})")
        sample_indices = result["outlier_indices"][:5]
        print(f"  {result['outlier_count']} anomalies (rows: {sample_indices}{'...' if len(result['outlier_indices']) > 5 else ''})")
        print()

def generate_html_report(filepath: str, df, missing_results: dict, duplicate_results: dict,
                          rule_results: list, outlier_results: list, score_result: dict,
                          output_path: str = "quality_report.html"):
    total_rows = len(df)
    total_cols = len(df.columns)
    total_missing = sum(v["missing_count"] for v in missing_results.values())
    total_cells = total_rows * total_cols
    missing_pct = round((total_missing / total_cells) * 100, 2) if total_cells else 0

    score = score_result["score"]
    score_color = "#2ecc71" if score >= 90 else "#f39c12" if score >= 70 else "#e74c3c"

    rows_html = ""
    for result in rule_results:
        if "error" in result or result["invalid_count"] == 0:
            continue
        rows_html += f"<tr><td>{result['column']}</td><td>Invalid value</td><td>{result['invalid_count']}</td></tr>"

    for result in outlier_results:
        if "error" in result or "note" in result or result["outlier_count"] == 0:
            continue
        rows_html += f"<tr><td>{result['column']}</td><td>Statistical outlier ({result['method']})</td><td>{result['outlier_count']}</td></tr>"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Data Quality Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f7f7f9; color: #222; }}
            .card {{ background: white; border-radius: 8px; padding: 24px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            .score {{ font-size: 48px; font-weight: bold; color: {score_color}; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
            th, td {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid #eee; }}
            th {{ background: #fafafa; }}
            .metric {{ display: inline-block; margin-right: 40px; }}
            .metric-label {{ color: #777; font-size: 13px; }}
            .metric-value {{ font-size: 22px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Data Quality Report</h1>
        <p><b>File:</b> {filepath}</p>

        <div class="card">
            <div class="score">{score} / 100</div>
            <p>Overall Quality Score</p>
        </div>

        <div class="card">
            <div class="metric">
                <div class="metric-label">Rows</div>
                <div class="metric-value">{total_rows:,}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Columns</div>
                <div class="metric-value">{total_cols}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Missing Values</div>
                <div class="metric-value">{missing_pct}%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Duplicate Rows</div>
                <div class="metric-value">{duplicate_results['duplicate_count']}</div>
            </div>
        </div>

        <div class="card">
            <h3>Detected Issues</h3>
            <table>
                <tr><th>Column</th><th>Issue Type</th><th>Count</th></tr>
                {rows_html if rows_html else "<tr><td colspan='3'>No issues detected</td></tr>"}
            </table>
        </div>
    </body>
    </html>
    """

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nHTML report saved to: {output_path}")