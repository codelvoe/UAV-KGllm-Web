from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class LoginBody(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(body: LoginBody):
    ok = body.username == "admin" and body.password == "123456"
    return {"success": ok, "token": "local-token" if ok else "", "username": body.username if ok else ""}
