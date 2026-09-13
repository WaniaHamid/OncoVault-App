import re
from typing import List, Optional
from models.request_response import OtherClinicalFields

def extract_other_fields_from_text(doc, raw_text: str) -> OtherClinicalFields:
    other = OtherClinicalFields()
    
    # 1. Blast cell percentage
    blast_match = re.search(r"\b([0-9]+(?:\.[0-9]+)?)\s*(?:%|percent)?\s*(?:blasts?|blast cells?)\b|\b(?:blasts?|blast cells?)\s*(?:is|was|of|:|=|\bat\b)?\s*([0-9]+(?:\.[0-9]+)?)\s*%?", raw_text, re.IGNORECASE)
    if blast_match:
        val_str = blast_match.group(1) or blast_match.group(2)
        try:
            other.blastCellPercentage = float(val_str)
        except ValueError:
            pass
            
    # 2. Disease type & Subtype (AML, ALL, CML, CLL, Multiple Myeloma, etc.)
    # Check that it is about the patient and not family history
    # Split by sentence to isolate
    sentences = [sent.text for sent in doc.sents] if hasattr(doc, "sents") else [raw_text]
    for sent in sentences:
        sent_lower = sent.lower()
        if re.search(r"\b(?:mother|father|sister|brother|parent|family)\b", sent_lower):
            continue  # Skip family history sentences
            
        if "acute myeloid leukemia" in sent_lower or re.search(r"\baml\b", sent_lower):
            other.diseaseType = "Acute Leukemia"
            other.diagnosisSubtype = "AML"
        elif "acute lymphoblastic leukemia" in sent_lower or re.search(r"\ball\b", sent_lower):
            other.diseaseType = "Acute Leukemia"
            other.diagnosisSubtype = "ALL"
        elif "chronic myeloid leukemia" in sent_lower or re.search(r"\bcml\b", sent_lower):
            other.diseaseType = "Chronic Leukemia"
            other.diagnosisSubtype = "CML"
        elif "chronic lymphocytic leukemia" in sent_lower or re.search(r"\bcll\b", sent_lower):
            other.diseaseType = "Chronic Leukemia"
            other.diagnosisSubtype = "CLL"
        elif "multiple myeloma" in sent_lower or re.search(r"\bmyeloma\b", sent_lower):
            other.diseaseType = "Multiple Myeloma"
            other.diagnosisSubtype = "Multiple Myeloma"
        elif "hodgkin" in sent_lower:
            other.diseaseType = "Lymphoma"
            other.diagnosisSubtype = "Hodgkin Lymphoma"
        elif "non-hodgkin" in sent_lower or "nhl" in sent_lower:
            other.diseaseType = "Lymphoma"
            other.diagnosisSubtype = "Non-Hodgkin Lymphoma"
            
        # Staging
        stage_match = re.search(r"\b(?:stage\s+(?:i{1,4}|[1-4]|iv)|rai\s+stage\s+[0-4]|binet\s+stage\s+[abc]|intermediate\s+risk|high\s+risk|standard\s+risk)\b", sent_lower)
        if stage_match:
            other.stage = stage_match.group(0).title()
            
        # Status
        if "in remission" in sent_lower:
            other.diagnosisStatus = "In Remission"
        elif "relapsed" in sent_lower or "relapse" in sent_lower:
            other.diagnosisStatus = "Relapsed"
        elif "newly diagnosed" in sent_lower:
            other.diagnosisStatus = "Newly Diagnosed"
        elif "active disease" in sent_lower:
            other.diagnosisStatus = "Active"
            
    # 3. Chemotherapy regimen
    chemo_match = re.search(r"\b(?:7\+3|hidac|hyper-cvad|abvd|chop|r-chop|flag-ida|daunorubicin|cytarabine)\b", raw_text, re.IGNORECASE)
    if chemo_match:
        other.chemotherapy = chemo_match.group(0).upper()
        
    # 4. Bone marrow biopsy
    bm_match = re.search(r"(?:bone marrow(?:\s+biopsy)?\s+(?:shows|reveals|demonstrates|indicates|finding:?)[^\.\;]+)", raw_text, re.IGNORECASE)
    if bm_match:
        other.boneMarrowBiopsy = bm_match.group(0).strip()
        
    return other
