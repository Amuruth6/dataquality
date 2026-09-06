def compute_quality_score(total_rows: int, total_cells: int, missing_results: dict,
                           duplicate_results: dict, invalid_results: list, outlier_results: list) -> dict:
    """
    Compute an overall data quality score (0-100) using a weighted deduction model.

    Weights reflect real-world severity:
    - Missing values (weight 0.25): common and often expected, lower penalty
    - Duplicate rows (weight 0.25): indicates pipeline/ingestion issues
    - Invalid values - type/range/regex violations (weight 0.35): most severe,
      these are actively wrong values, not just absent ones
    - Statistical outliers (weight 0.15): may be legitimate rare events, so
      weighted lowest - flagged for review, not treated as definite errors
    """
    total_missing = sum(v["missing_count"] for v in missing_results.values())
    missing_ratio = total_missing / total_cells if total_cells else 0

    duplicate_ratio = duplicate_results["duplicate_count"] / total_rows if total_rows else 0

    total_invalid = sum(r.get("invalid_count", 0) for r in invalid_results)
    total_checked_cells = total_rows * len(invalid_results) if invalid_results else 1
    invalid_ratio = total_invalid / total_checked_cells if total_checked_cells else 0

    total_outliers = sum(r.get("outlier_count", 0) for r in outlier_results)
    outlier_ratio = total_outliers / total_rows if total_rows else 0

    missing_penalty = min(25, missing_ratio * 100 * 0.25)
    duplicate_penalty = min(25, duplicate_ratio * 100 * 0.25)
    invalid_penalty = min(35, invalid_ratio * 100 * 0.35)
    outlier_penalty = min(15, outlier_ratio * 100 * 0.15)

    total_penalty = missing_penalty + duplicate_penalty + invalid_penalty + outlier_penalty
    score = max(0, round(100 - total_penalty, 1))

    return {
        "score": score,
        "breakdown": {
            "missing_penalty": round(missing_penalty, 2),
            "duplicate_penalty": round(duplicate_penalty, 2),
            "invalid_penalty": round(invalid_penalty, 2),
            "outlier_penalty": round(outlier_penalty, 2),
        }
    }