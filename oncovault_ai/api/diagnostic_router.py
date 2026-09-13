"""
OncoVault AI Engine - FastAPI Diagnostic Router
Provides endpoints for independent Symptom and CBC Leukemia Risk Assessments.
"""
from fastapi import APIRouter, HTTPException, status
import logging
from typing import Dict, Any

from .schemas import (
    SymptomRiskRequest,
    CbcRiskRequest,
    RiskAssessmentResponse
)
from ..src.predict import DiagnosticEngine

logger = logging.getLogger("oncovault_diagnostic_engine")
router = APIRouter(prefix="", tags=["AI Diagnostic Engine"])

@router.post(
    "/predict-symptoms",
    response_model=RiskAssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Symptom Leukemia Risk Assessment",
    description="Estimates leukemia risk and identifies key contributing symptoms using the finalized 16-symptom decision-support model."
)
async def predict_symptoms(req: SymptomRiskRequest) -> RiskAssessmentResponse:
    try:
        engine = DiagnosticEngine.get_instance()
        data = req.to_canonical_dict()
        result = engine.assess_symptoms(data)
        return RiskAssessmentResponse(**result)
    except RuntimeError as e:
        logger.error(f"Symptom Model Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Symptom Prediction Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Symptom risk assessment failed: {str(e)}"
        )

@router.post(
    "/predict-cbc",
    response_model=RiskAssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="CBC Leukemia Risk Assessment",
    description="Estimates leukemia risk and highlights key hematologic factors using the finalized 9-feature CBC decision-support model."
)
async def predict_cbc(req: CbcRiskRequest) -> RiskAssessmentResponse:
    try:
        engine = DiagnosticEngine.get_instance()
        data = req.to_canonical_dict()
        result = engine.assess_cbc(data)
        return RiskAssessmentResponse(**result)
    except RuntimeError as e:
        logger.error(f"CBC Model Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"CBC Prediction Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CBC risk assessment failed: {str(e)}"
        )
