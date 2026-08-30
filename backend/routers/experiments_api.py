from fastapi import APIRouter

from services.experiment_service import detection_results, efficiency_results, performance_summary, robustness_results

router = APIRouter()


@router.get("/detection")
def detection():
    return detection_results()


@router.get("/efficiency")
def efficiency():
    return efficiency_results()


@router.get("/robustness")
def robustness():
    return robustness_results()


@router.get("/summary")
def summary():
    return performance_summary()
