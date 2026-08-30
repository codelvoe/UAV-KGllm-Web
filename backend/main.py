from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth_api, dashboard_api, data_api, tracks_api, kg_api, fusion_api
from routers import llm_api, chat_api, experiments_api, settings_api, catalog_api, yolo_detection
from services.data_loader import ensure_runtime_data


app = FastAPI(title="基于知识图谱与大模型的无人机多源感知融合分析系统 V1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ensure_runtime_data()

app.include_router(auth_api.router, prefix="/api/auth", tags=["auth"])
app.include_router(dashboard_api.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(data_api.router, prefix="/api/data", tags=["data"])
app.include_router(tracks_api.router, prefix="/api/tracks", tags=["tracks"])
app.include_router(kg_api.router, prefix="/api/kg", tags=["kg"])
app.include_router(fusion_api.router, prefix="/api/fusion", tags=["fusion"])
app.include_router(llm_api.router, prefix="/api/llm", tags=["llm"])
app.include_router(chat_api.router, prefix="/api/chat", tags=["chat"])
app.include_router(experiments_api.router, prefix="/api/experiments", tags=["experiments"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["settings"])
app.include_router(catalog_api.router, prefix="/api/catalog", tags=["catalog"])
app.include_router(yolo_detection.router, prefix="/api/yolo", tags=["yolo"])


@app.get("/")
def health():
    return {"status": "ok", "system": "UAV-KGLLM-Web"}
