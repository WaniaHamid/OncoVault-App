import pytest
from nlp.pipeline import ClinicalNlpPipeline

@pytest.fixture
def pipeline():
    return ClinicalNlpPipeline()

def test_negated_symptom(pipeline):
    res = pipeline.process("Patient denies fever.")
    assert "fever" in res.symptoms
    assert res.symptoms["fever"].value is False
    assert res.symptoms["fever"].status == "negated"

def test_no_bone_pain(pipeline):
    res = pipeline.process("There is no bone pain.")
    assert "bonePain" in res.symptoms
    assert res.symptoms["bonePain"].value is False
    assert res.symptoms["bonePain"].status == "negated"

def test_mixed_positive_and_negated(pipeline):
    res = pipeline.process("Patient has persistent fatigue and fever but denies bone pain. WBC is 14.5 k/uL.")
    assert res.symptoms["persistentWeaknessAndFatigue"].value is True
    assert res.symptoms["fever"].value is True
    assert res.symptoms["bonePain"].value is False
    assert res.symptoms["bonePain"].status == "negated"
    assert res.cbc.wbc.value == 14.5
