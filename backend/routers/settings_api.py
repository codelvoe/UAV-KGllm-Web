from fastapi import APIRouter

from services.settings_service import get_settings as load_settings, save_settings as persist_settings

router = APIRouter()


@router.get("")
def get_settings():
    return load_settings()


@router.post("")
def save_settings(settings: dict):
    return persist_settings(settings)
