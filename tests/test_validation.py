from oncology_platform.generate_data import generate_synthetic_data
from oncology_platform.validation import validate_tables


def test_valid_data_passes_all_rules():
    result = validate_tables(generate_synthetic_data(75, 21))
    assert not (result.status == "fail").any()


def test_duplicate_and_invalid_date_are_detected():
    tables = generate_synthetic_data(30, 11)
    tables["patients"] = __import__("pandas").concat([tables["patients"], tables["patients"].iloc[[0]]], ignore_index=True)
    tables["treatment_events"].loc[0, "treatment_end_date"] = "1900-01-01"
    result = validate_tables(tables).set_index("rule")
    assert result.loc["patient_id_unique", "status"] == "fail"
    assert result.loc["treatment_date_order", "status"] == "fail"


def test_missing_optional_values_do_not_fail_required_rules():
    tables = generate_synthetic_data(50, 2)
    tables["diagnoses"].loc[:4, "biomarker_status"] = None
    assert (validate_tables(tables).status == "pass").all()

