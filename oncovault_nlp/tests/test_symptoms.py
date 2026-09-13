import pytest
from nlp.pipeline import ClinicalNlpPipeline

@pytest.fixture
def pipeline():
    return ClinicalNlpPipeline()

def test_single_positive_symptom(pipeline):
    res = pipeline.process("Patient has fever.")
    assert "fever" in res.symptoms
    assert res.symptoms["fever"].value is True
    assert res.symptoms["fever"].status == "present"

def test_multiple_symptoms(pipeline):
    res = pipeline.process("Patient has persistent fatigue, fever and night sweats.")
    assert "persistentWeaknessAndFatigue" in res.symptoms
    assert res.symptoms["persistentWeaknessAndFatigue"].value is True
    
    assert "fever" in res.symptoms
    assert res.symptoms["fever"].value is True
    
    assert "nightSweats" in res.symptoms
    assert res.symptoms["nightSweats"].value is True
