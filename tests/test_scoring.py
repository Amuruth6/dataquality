from dataquality.scoring import compute_quality_score


def test_perfect_data_scores_100():
    missing_results = {"col": {"missing_count": 0, "missing_pct": 0.0}}
    duplicate_results = {"duplicate_count": 0}
    result = compute_quality_score(
        total_rows=100, total_cells=100,
        missing_results=missing_results,
        duplicate_results=duplicate_results,
        invalid_results=[], outlier_results=[]
    )
    assert result["score"] == 100


def test_score_never_goes_below_zero():
    missing_results = {"col": {"missing_count": 1000, "missing_pct": 100.0}}
    duplicate_results = {"duplicate_count": 1000}
    invalid_results = [{"invalid_count": 1000}]
    outlier_results = [{"outlier_count": 1000}]
    result = compute_quality_score(
        total_rows=10, total_cells=10,
        missing_results=missing_results,
        duplicate_results=duplicate_results,
        invalid_results=invalid_results,
        outlier_results=outlier_results
    )
    assert result["score"] >= 0


def test_score_breakdown_keys_present():
    result = compute_quality_score(
        total_rows=10, total_cells=10,
        missing_results={}, duplicate_results={"duplicate_count": 0},
        invalid_results=[], outlier_results=[]
    )
    expected_keys = {"missing_penalty", "duplicate_penalty", "invalid_penalty", "outlier_penalty"}
    assert set(result["breakdown"].keys()) == expected_keys