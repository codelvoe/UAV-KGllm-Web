from fastapi import APIRouter, Query
from services.data_loader import modal_records

router = APIRouter()


@router.get("/modalities")
def modalities():
    return [
        {"source": "radar", "records": 15362, "role": "空间/运动候选"},
        {"source": "spectrum", "records": 445, "role": "无线电语义证据"},
        {"source": "recognize", "records": 166, "role": "视觉识别证据"},
        {"source": "pho_status", "records": 422, "role": "光电状态/视线"},
        {"source": "decrypt", "records": 422, "role": "隐藏伪标签"},
    ]


@router.get("/records")
def records(source: str = "radar", page: int = 1, page_size: int = 20, keyword: str = ""):
    return modal_records(source, page, page_size, keyword)


@router.get("/records/{record_id}")
def record_detail(record_id: str, source: str = Query("radar")):
    data = modal_records(source, 1, 10000)["items"]
    found = next((r for r in data if r["record_id"] == record_id), None)
    return found or {"record_id": record_id, "message": "not found"}
