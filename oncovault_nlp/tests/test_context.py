import pytest
from nlp.pipeline import ClinicalNlpPipeline

@pytest.fixture
def pipeline():
    return ClinicalNlpPipeline()

def test_family_history_isolation(pipeline):
    res = pipeline.process("Patient's mother had leukemia.")
    # Must NOT become patient diagnosis
    assert res.other.diagnosisSubtype is None or res.other.diagnosisSubtype == ""
    # Can map to familyHistory symptom
    assert "familyHistory" in res.symptoms
    assert res.symptoms["familyHistory"].value is True
