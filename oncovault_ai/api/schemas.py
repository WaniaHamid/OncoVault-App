"""
OncoVault AI Engine - Pydantic Request & Response Schemas
"""
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator

class SymptomRiskRequest(BaseModel):
    # 16 Finalized OncoVault Symptoms
    shortness_of_breath: Optional[Union[int, bool]] = Field(0, description="Shortness of breath (0 or 1 / bool)")
    bone_pain: Optional[Union[int, bool]] = Field(0, description="Bone pain (0 or 1 / bool)")
    fever: Optional[Union[int, bool]] = Field(0, description="Fever (0 or 1 / bool)")
    family_history: Optional[Union[int, bool]] = Field(0, description="Family history of cancer (0 or 1 / bool)")
    frequent_infections: Optional[Union[int, bool]] = Field(0, description="Frequent infections (0 or 1 / bool)")
    itchy_skin_rash: Optional[Union[int, bool]] = Field(0, description="Itchy skin or rash (0 or 1 / bool)")
    loss_of_appetite_nausea: Optional[Union[int, bool]] = Field(0, description="Loss of appetite or nausea (0 or 1 / bool)")
    persistent_weakness_fatigue: Optional[Union[int, bool]] = Field(0, description="Persistent weakness and fatigue (0 or 1 / bool)")
    swollen_painless_lymph_nodes: Optional[Union[int, bool]] = Field(0, description="Swollen painless lymph nodes (0 or 1 / bool)")
    significant_bruising_bleeding: Optional[Union[int, bool]] = Field(0, description="Significant bruising or bleeding (0 or 1 / bool)")
    enlarged_liver: Optional[Union[int, bool]] = Field(0, description="Enlarged liver (0 or 1 / bool)")
    oral_cavity_changes: Optional[Union[int, bool]] = Field(0, description="Oral cavity changes (0 or 1 / bool)")
    vision_blurring: Optional[Union[int, bool]] = Field(0, description="Vision blurring (0 or 1 / bool)")
    jaundice: Optional[Union[int, bool]] = Field(0, description="Jaundice (0 or 1 / bool)")
    night_sweats: Optional[Union[int, bool]] = Field(0, description="Night sweats (0 or 1 / bool)")
    smoking_history: Optional[Union[int, bool]] = Field(0, description="Smoking history (0 or 1 / bool)")

    # Support camelCase aliases passed from Flutter EHR
    shortnessOfBreath: Optional[Union[int, bool]] = None
    bonePain: Optional[Union[int, bool]] = None
    familyHistory: Optional[Union[int, bool]] = None
    frequentInfections: Optional[Union[int, bool]] = None
    itchySkinOrRash: Optional[Union[int, bool]] = None
    lossOfAppetiteOrNausea: Optional[Union[int, bool]] = None
    persistentWeaknessAndFatigue: Optional[Union[int, bool]] = None
    swollenPainlessLymphNodes: Optional[Union[int, bool]] = None
    significantBruisingOrBleeding: Optional[Union[int, bool]] = None
    enlargedLiver: Optional[Union[int, bool]] = None
    oralCavityChanges: Optional[Union[int, bool]] = None
    visionBlurring: Optional[Union[int, bool]] = None
    nightSweats: Optional[Union[int, bool]] = None
    smokes: Optional[Union[int, bool]] = None

    def to_canonical_dict(self) -> Dict[str, int]:
        d = {
            "shortness_of_breath": int(bool(self.shortnessOfBreath if self.shortnessOfBreath is not None else self.shortness_of_breath)),
            "bone_pain": int(bool(self.bonePain if self.bonePain is not None else self.bone_pain)),
            "fever": int(bool(self.fever)),
            "family_history": int(bool(self.familyHistory if self.familyHistory is not None else self.family_history)),
            "frequent_infections": int(bool(self.frequentInfections if self.frequentInfections is not None else self.frequent_infections)),
            "itchy_skin_rash": int(bool(self.itchySkinOrRash if self.itchySkinOrRash is not None else self.itchy_skin_rash)),
            "loss_of_appetite_nausea": int(bool(self.lossOfAppetiteOrNausea if self.lossOfAppetiteOrNausea is not None else self.loss_of_appetite_nausea)),
            "persistent_weakness_fatigue": int(bool(self.persistentWeaknessAndFatigue if self.persistentWeaknessAndFatigue is not None else self.persistent_weakness_fatigue)),
            "swollen_painless_lymph_nodes": int(bool(self.swollenPainlessLymphNodes if self.swollenPainlessLymphNodes is not None else self.swollen_painless_lymph_nodes)),
            "significant_bruising_bleeding": int(bool(self.significantBruisingOrBleeding if self.significantBruisingOrBleeding is not None else self.significant_bruising_bleeding)),
            "enlarged_liver": int(bool(self.enlargedLiver if self.enlargedLiver is not None else self.enlarged_liver)),
            "oral_cavity_changes": int(bool(self.oralCavityChanges if self.oralCavityChanges is not None else self.oral_cavity_changes)),
            "vision_blurring": int(bool(self.visionBlurring if self.visionBlurring is not None else self.vision_blurring)),
            "jaundice": int(bool(self.jaundice)),
            "night_sweats": int(bool(self.nightSweats if self.nightSweats is not None else self.night_sweats)),
            "smoking_history": int(bool(self.smokes if self.smokes is not None else self.smoking_history)),
        }
        return d

class CbcRiskRequest(BaseModel):
    # 9 Finalized OncoVault CBC Features
    WBC: Optional[float] = Field(None, description="White Blood Cell Count (10^9/L)")
    RBC: Optional[float] = Field(None, description="Red Blood Cell Count (10^12/L)")
    HGB: Optional[float] = Field(None, description="Hemoglobin (g/L)")
    PLT: Optional[float] = Field(None, description="Platelets (10^9/L)")
    NEUT_ABS: Optional[float] = Field(None, description="Absolute Neutrophils (10^9/L)")
    NEUT_PCT: Optional[float] = Field(None, description="Neutrophil Percentage (%)")
    MONO_ABS: Optional[float] = Field(None, description="Absolute Monocytes (10^9/L)")
    RDW_SD: Optional[float] = Field(None, description="RDW-SD (fL)")
    RDW_CV: Optional[float] = Field(None, description="RDW-CV (%)")

    # Common aliases from EHR / Flutter
    wbc: Optional[float] = None
    rbc: Optional[float] = None
    hemoglobin: Optional[float] = None
    platelets: Optional[float] = None
    neutrophils_abs: Optional[float] = None
    neutrophils_pct: Optional[float] = None
    monocytes_abs: Optional[float] = None
    rdwSd: Optional[float] = None
    rdwCv: Optional[float] = None

    def to_canonical_dict(self) -> Dict[str, float]:
        return {
            "WBC": float(self.WBC if self.WBC is not None else (self.wbc or 0.0)),
            "RBC": float(self.RBC if self.RBC is not None else (self.rbc or 0.0)),
            "HGB": float(self.HGB if self.HGB is not None else (self.hemoglobin or 0.0)),
            "PLT": float(self.PLT if self.PLT is not None else (self.platelets or 0.0)),
            "NEUT_ABS": float(self.NEUT_ABS if self.NEUT_ABS is not None else (self.neutrophils_abs or 0.0)),
            "NEUT_PCT": float(self.NEUT_PCT if self.NEUT_PCT is not None else (self.neutrophils_pct or 0.0)),
            "MONO_ABS": float(self.MONO_ABS if self.MONO_ABS is not None else (self.monocytes_abs or 0.0)),
            "RDW_SD": float(self.RDW_SD if self.RDW_SD is not None else (self.rdwSd or 0.0)),
            "RDW_CV": float(self.RDW_CV if self.RDW_CV is not None else (self.rdwCv or 0.0)),
        }

class RiskAssessmentResponse(BaseModel):
    prediction: str = Field(..., description="'Elevated Risk' or 'Lower Risk'")
    riskScore: float = Field(..., description="Estimated risk score between 0.0 and 1.0")
    modelVersion: str = Field(..., description="Model version tag, e.g. leukemia-symptom-v1 or leukemia-cbc-v1")
    contributingFactors: List[str] = Field(default_factory=list, description="Top contributing clinical features")
    analyzedAt: str = Field(..., description="ISO 8601 UTC timestamp")
    disclaimer: str = Field(..., description="Clinical decision support disclaimer")
