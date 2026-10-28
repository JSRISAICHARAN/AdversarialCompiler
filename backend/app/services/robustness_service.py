
from backend.app.services.ml_detector import predict_source
from backend.app.services.compiler_service import compile_c_source


def run_robustness_probe(source_code: str) -> dict:
    """
    Compare ML predictions after simple source formatting changes.
    Does not execute the submitted C program.
    """

    variants = {
        "original": source_code,
        "trailing_newline": source_code.rstrip("\n") + "\n",
        "extra_blank_lines": source_code + "\n\n",
        "leading_comment": "/* Robustness probe */\n" + source_code,
    }

    results = []

    for name, transformed_source in variants.items():
        prediction = predict_source(transformed_source)
        compilation = compile_c_source(transformed_source)

        results.append({
            "transformation": name,
            "prediction_available": prediction.get("available", False),
            "predicted_label": prediction.get("predicted_label"),
            "predicted_class": prediction.get("predicted_class"),
            "class_probabilities": prediction.get("class_probabilities"),
            "compiled": compilation.get("compiled", False),
            "compiler_return_code": compilation.get("return_code"),
            "compiler_diagnostics": compilation.get("stderr", ""),
        })

    baseline_label = results[0]["predicted_label"]
    baseline_available = results[0]["prediction_available"]

    for result in results:
        result["prediction_changed"] = (
            baseline_available
            and result["prediction_available"]
            and result["predicted_label"] != baseline_label
        )

    available_results = [
        result for result in results
        if result["prediction_available"]
    ]

    changed_count = sum(
        result["prediction_changed"] for result in results
    )

    return {
        "status": "completed",
        "experiment": "Formatting-based robustness probe",
        "variants_tested": len(results),
        "baseline_label": baseline_label,
        "prediction_changes": changed_count,
        "robustness_rate": (
            round(
                1 - changed_count / len(available_results), 4
            )
            if available_results else None
        ),
        "results": results,
        "warning": (
            "Preliminary experiment only. Prediction stability does not "
            "prove semantic equivalence or security. Compilation success "
            "does not prove that the program is safe."
        ),
    }
