from fastapi import APIRouter
from pydantic import BaseModel

from services.report_service import add_report_item, clear_report_draft, generate_report, get_report_draft

router = APIRouter()


class ReportItem(BaseModel):
    type: str
    title: str
    content: str


@router.post("/add-item")
def add_item(item: ReportItem):
    return add_report_item(item.dict())


@router.get("/draft")
def draft():
    return get_report_draft()


@router.post("/generate")
def generate():
    return generate_report()


@router.delete("/clear")
def clear():
    return clear_report_draft()
