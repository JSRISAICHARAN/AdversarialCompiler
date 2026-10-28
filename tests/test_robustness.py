
from backend.app.services.robustness_service import run_robustness_probe


def test_robustness_probe_returns_expected_structure():
    source = """
#include <stdio.h>
int main(void) {
    printf("Hello\\n");
    return 0;
}
"""
    result = run_robustness_probe(source)

    assert result["status"] == "completed"
    assert result["variants_tested"] == 4
    assert len(result["results"]) == 4
    assert "prediction_changes" in result
    assert "robustness_rate" in result


def test_robustness_probe_includes_original_variant():
    source = "int main(void) { return 0; }"
    result = run_robustness_probe(source)

    assert result["results"][0]["transformation"] == "original"
    assert result["results"][0]["prediction_available"] is True
