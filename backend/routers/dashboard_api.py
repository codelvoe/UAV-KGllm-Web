from fastapi import APIRouter

from services.dashboard_service import (
    dashboard_charts,
    dashboard_summary,
    experiment_overview,
    quality_summary,
)

router = APIRouter()


@router.get("/summary")
def summary():
    return dashboard_summary()


@router.get("/charts")
def charts():
    return dashboard_charts()


@router.get("/quality")
def quality():
    return quality_summary()


@router.get("/experiment-summary")
def experiment_summary_api():
    return experiment_overview()
