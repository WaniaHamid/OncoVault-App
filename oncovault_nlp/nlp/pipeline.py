import spacy
from typing import Dict, Any, List
from models.request_response import ExtractResponse, CbcExtraction, OtherClinicalFields
from .symptom_extractor import extract_symptoms_from_text
from .cbc_extractor import extract_cbc_from_text
from .other_extractor import extract_other_fields_from_text
from .normalizer import normalize_text

class ClinicalNlpPipeline:
    def __init__(self):
        try:
            # Use blank english with sentencizer for fast, reliable tokenization & sentence boundaries
            self.nlp = spacy.blank("en")
            if "sentencizer" not in self.nlp.pipe_names:
                self.nlp.add_pipe("sentencizer")
        except Exception as e:
            print(f"Warning: Could not initialize custom spacy pipeline: {e}")
            self.nlp = None

    def process(self, text: str) -> ExtractResponse:
        cleaned_text = normalize_text(text)
        warnings: List[str] = []
        
        if not cleaned_text:
            return ExtractResponse(
                text="",
                symptoms={},
                cbc=CbcExtraction(),
                other=OtherClinicalFields(),
                warnings=["Empty input text provided."]
            )
            
        doc = self.nlp(cleaned_text) if self.nlp else None
        
        # 1. Extract symptoms
        symptoms = extract_symptoms_from_text(doc, cleaned_text)
        
        # 2. Extract CBC laboratory findings
        cbc = extract_cbc_from_text(doc, cleaned_text)
        
        # 3. Extract other clinical findings (staging, subtype, chemo, bone marrow)
        other = extract_other_fields_from_text(doc, cleaned_text)
        
        # Add original notes
        other.clinicalNotes = cleaned_text
        
        return ExtractResponse(
            text=cleaned_text,
            symptoms=symptoms,
            cbc=cbc,
            other=other,
            warnings=warnings
        )
