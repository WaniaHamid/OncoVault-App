import pytest
from nlp.pipeline import ClinicalNlpPipeline

@pytest.fixture
def pipeline():
    return ClinicalNlpPipeline()

def test_cbc_basic(pipeline):
    res = pipeline.process("WBC is 14.5 k/uL, hemoglobin is 10.2 g/dL and platelets are 110 k/uL.")
    assert res.cbc.wbc is not None
    assert res.cbc.wbc.value == 14.5
    assert res.cbc.wbc.unit == "k/uL"
    
    assert res.cbc.hemoglobin is not None
    assert res.cbc.hemoglobin.value == 10.2
    assert res.cbc.hemoglobin.unit == "g/dL"
    
    assert res.cbc.platelets is not None
    assert res.cbc.platelets.value == 110.0

def test_missing_fields_not_fabricated(pipeline):
    res = pipeline.process("WBC is 14.5.")
    assert res.cbc.wbc is not None
    assert res.cbc.wbc.value == 14.5
    assert res.cbc.rbc is None
    assert res.cbc.hemoglobin is None
    assert res.cbc.platelets is None
