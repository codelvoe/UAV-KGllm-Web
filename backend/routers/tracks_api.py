from fastapi import APIRouter

from services.track_service import build_track_features, get_track_detail, list_tracks

router = APIRouter()


@router.get("")
def tracks(source: str = "", target_type: str = ""):
    return list_tracks(source, target_type)


@router.get("/{track_id}")
def track_detail(track_id: str):
    return get_track_detail(track_id)


@router.get("/{track_id}/features")
def track_features(track_id: str):
    return build_track_features(track_id)
