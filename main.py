import click
import yaml

from dataquality.ingestion import load_data
from dataquality.validators import check_missing_values, check_duplicates, check_range, check_regex, check_dtype
from dataquality.anomaly import detect_outliers_iqr, detect_outliers_zscore
from dataquality.scoring import compute_quality_score
from dataquality.report import print_console_report
from dataquality.report import print_console_report, generate_html_report


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


@click.command()
@click.option("--config", default="config.yaml", help="Path to config YAML file.")
def run(config):
    """Run a data quality analysis based on the given config file."""
    cfg = load_config(config)
    filepath = cfg["file"]
    rules = cfg.get("rules", {})

    df = load_data(filepath)

    missing_results = check_missing_values(df)
    duplicate_results = check_duplicates(df, ignore_columns=cfg.get("duplicate_check", {}).get("ignore_columns", []))

    rule_results = []
    outlier_results = []

    for column, rule in rules.items():
        if "min" in rule or "max" in rule:
            rule_results.append(check_range(df, column, rule.get("min"), rule.get("max")))
        elif "regex" in rule:
            rule_results.append(check_regex(df, column, rule["regex"]))
        elif "type" in rule and "outlier_method" not in rule:
            rule_results.append(check_dtype(df, column, rule["type"]))

        if rule.get("outlier_method") == "iqr":
            outlier_results.append(detect_outliers_iqr(df, column))
        elif rule.get("outlier_method") == "zscore":
            outlier_results.append(detect_outliers_zscore(df, column))

    score_result = compute_quality_score(
        total_rows=len(df),
        total_cells=len(df) * len(df.columns),
        missing_results=missing_results,
        duplicate_results=duplicate_results,
        invalid_results=rule_results,
        outlier_results=outlier_results
    )

    print_console_report(filepath, df, missing_results, duplicate_results, rule_results, outlier_results, score_result)
    print_console_report(filepath, df, missing_results, duplicate_results, rule_results, outlier_results, score_result)
    generate_html_report(filepath, df, missing_results, duplicate_results, rule_results, outlier_results, score_result)


if __name__ == "__main__":
    run()