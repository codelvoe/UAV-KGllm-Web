from __future__ import annotations

import base64
import io
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import requests
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFont

from services.data_loader import DATA_DIR, read_json

router = APIRouter()

YOLO_ROOT = Path(__file__).resolve().parents[1] / "services" / "yoloDetection"
SAMPLE_DIR = YOLO_ROOT / "datasample"
MODEL_PATH = YOLO_ROOT / "models" / "best.pt"
LOCAL_ULTRALYTICS_PARENT = YOLO_ROOT
YOLO_CONFIG_DIR = Path(__file__).resolve().parents[1] / "data" / "ultralytics_config"
YOLO_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("YOLO_CONFIG_DIR", str(YOLO_CONFIG_DIR))

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VIDEO_SUFFIXES = {".avi", ".mp4", ".mov", ".mkv", ".wmv"}

_MODEL = None
_MODEL_ERROR = ""


class AnalysisBody(BaseModel):
    summary: dict[str, Any]


def _safe_sample_path(kind: str, name: str) -> Path:
    path = (SAMPLE_DIR / name).resolve()
    if SAMPLE_DIR.resolve() not in path.parents or not path.exists():
        raise HTTPException(status_code=404, detail="本地素材文件不存在")
    suffixes = IMAGE_SUFFIXES if kind == "image" else VIDEO_SUFFIXES
    if path.suffix.lower() not in suffixes:
        raise HTTPException(status_code=400, detail="文件类型不匹配")
    return path


def _list_samples() -> dict[str, list[dict[str, str]]]:
    files = sorted(SAMPLE_DIR.glob("*")) if SAMPLE_DIR.exists() else []
    images = [
        {"name": item.name, "url": f"/api/yolo/sample/image/{item.name}"}
        for item in files
        if item.suffix.lower() in IMAGE_SUFFIXES
    ]
    videos = [
        {"name": item.name, "url": f"/api/yolo/sample/video/{item.name}"}
        for item in files
        if item.suffix.lower() in VIDEO_SUFFIXES
    ]
    return {"images": images, "videos": videos}


def _device_name() -> str:
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def _load_model():
    global _MODEL, _MODEL_ERROR
    if _MODEL is not None:
        return _MODEL
    if not MODEL_PATH.exists():
        _MODEL_ERROR = f"模型文件不存在: {MODEL_PATH}"
        raise HTTPException(status_code=500, detail=_MODEL_ERROR)
    try:
        local_path = str(LOCAL_ULTRALYTICS_PARENT)
        if local_path not in sys.path:
            sys.path.insert(0, local_path)
        from ultralytics import YOLO

        _MODEL = YOLO(str(MODEL_PATH))
        _MODEL_ERROR = ""
        return _MODEL
    except Exception as exc:
        _MODEL_ERROR = str(exc)
        raise HTTPException(status_code=500, detail=f"YOLO 模型加载失败: {exc}")


def _image_to_data_url(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=90)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def _read_image_bytes(data: bytes) -> Image.Image:
    try:
        return Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"图片读取失败: {exc}")


def _detect_pil(image: Image.Image, confidence: float, iou: float) -> dict[str, Any]:
    started = time.perf_counter()
    model = _load_model()
    results = model.predict(image, conf=confidence, iou=iou, device=_device_name(), verbose=False)
    result = results[0]
    width, height = image.size
    names = getattr(result, "names", {}) or {}
    detections = []
    boxes = getattr(result, "boxes", None)
    if boxes is not None:
        for idx, box in enumerate(boxes):
            xyxy = [float(value) for value in box.xyxy[0].tolist()]
            conf = float(box.conf[0].item()) if box.conf is not None else 0.0
            cls_id = int(box.cls[0].item()) if box.cls is not None else -1
            class_name = str(names.get(cls_id, f"class_{cls_id}"))
            x1, y1, x2, y2 = xyxy
            detections.append(
                {
                    "id": f"D{idx + 1:02d}",
                    "class_id": cls_id,
                    "class_name": class_name,
                    "confidence": round(conf, 4),
                    "bbox": [round(v, 2) for v in xyxy],
                    "center": [round((x1 + x2) / 2, 2), round((y1 + y2) / 2, 2)],
                    "area_ratio": round(max(0.0, (x2 - x1) * (y2 - y1)) / max(1, width * height), 6),
                }
            )
    annotated = _draw_detections(image.copy(), detections)
    max_conf = max((item["confidence"] for item in detections), default=0.0)
    return {
        "image_width": width,
        "image_height": height,
        "detections": detections,
        "detection_count": len(detections),
        "max_confidence": round(max_conf, 4),
        "annotated_image": _image_to_data_url(annotated),
        "runtime_sec": round(time.perf_counter() - started, 4),
    }


def _draw_detections(image: Image.Image, detections: list[dict[str, Any]]) -> Image.Image:
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    palette = ["#ff4d4f", "#fa8c16", "#1677ff", "#52c41a", "#722ed1"]
    for idx, det in enumerate(detections):
        x1, y1, x2, y2 = det["bbox"]
        color = palette[idx % len(palette)]
        draw.rectangle((x1, y1, x2, y2), outline=color, width=3)
        label = f"{det['class_name']} {det['confidence']:.2f}"
        text_box = draw.textbbox((x1, y1), label, font=font)
        text_w = text_box[2] - text_box[0]
        text_h = text_box[3] - text_box[1]
        draw.rectangle((x1, max(0, y1 - text_h - 8), x1 + text_w + 8, y1), fill=color)
        draw.text((x1 + 4, max(0, y1 - text_h - 5)), label, fill="white", font=font)
    return image


def _ollama_analysis(summary: dict[str, Any]) -> dict[str, Any]:
    settings = read_json(DATA_DIR / "settings.json", {})
    url = settings.get("ollama_url") or "http://localhost:11434/api/generate"
    model = settings.get("ollama_model") or "deepseek-r1:8b"
    prompt = f"""
你是无人机探测系统的辅助研判模块。请基于 YOLO 检测摘要给出中文研判，必须包括：
1. 意图识别；
2. 行为判断；
3. 告警等级；
4. 处置建议；
5. 不确定性说明。

检测摘要：
{summary}

要求：不要编造未提供的速度、身份、飞行轨迹；如果只有单帧图像，请明确说明只能做静态视觉研判。
""".strip()
    fallback = _rule_analysis(summary)
    try:
        response = requests.post(
            url,
            json={"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.25}},
            timeout=90,
        )
        response.raise_for_status()
        text = response.json().get("response", "").strip()
        return {
            "provider": "ollama",
            "model": model,
            "available": True,
            "conclusion": text or fallback["conclusion"],
            "fallback": False,
        }
    except Exception as exc:
        return {
            "provider": "rule-fallback",
            "model": model,
            "available": False,
            "conclusion": fallback["conclusion"],
            "fallback": True,
            "error": str(exc),
        }


def _rule_analysis(summary: dict[str, Any]) -> dict[str, str]:
    count = int(summary.get("detection_count") or summary.get("total_detections") or 0)
    max_conf = float(summary.get("max_confidence") or 0)
    if count == 0:
        level = "低"
        action = "未检测到明确无人机目标，建议继续观察或更换本地素材进行验证。"
    elif max_conf >= 0.75:
        level = "高"
        action = "检测到高置信目标，建议触发告警并联动多模态证据复核。"
    else:
        level = "中"
        action = "检测到疑似目标，建议结合雷达、频谱或人工复核降低误报风险。"
    return {
        "conclusion": (
            f"视觉检测共发现 {count} 个疑似目标，最高置信度 {max_conf:.2f}。"
            f"当前告警等级为{level}。意图识别方面，单帧或抽帧结果只能说明画面中存在疑似飞行目标，"
            f"不能独立判断飞行意图；行为判断需结合连续轨迹、速度和区域信息。{action}"
        )
    }


@router.get("/status")
def status():
    samples = _list_samples()
    ultralytics_ready = False
    error = ""
    try:
        local_path = str(LOCAL_ULTRALYTICS_PARENT)
        if local_path not in sys.path:
            sys.path.insert(0, local_path)
        import ultralytics  # noqa: F401

        ultralytics_ready = True
    except Exception as exc:
        error = str(exc)
    return {
        "model_exists": MODEL_PATH.exists(),
        "model_path": str(MODEL_PATH.relative_to(Path(__file__).resolve().parents[1])),
        "sample_images": samples["images"],
        "sample_videos": samples["videos"],
        "device": _device_name(),
        "ultralytics_ready": ultralytics_ready,
        "ultralytics_error": error,
        "model_loaded": _MODEL is not None,
        "model_error": _MODEL_ERROR,
    }


@router.get("/samples")
def samples():
    return _list_samples()


@router.get("/sample/image/{name}")
def sample_image(name: str):
    return FileResponse(_safe_sample_path("image", name))


@router.get("/sample/video/{name}")
def sample_video(name: str):
    return FileResponse(_safe_sample_path("video", name), media_type="video/x-msvideo")


@router.post("/detect/image")
async def detect_image(
    file: UploadFile | None = File(default=None),
    sample_name: str = Form(default=""),
    confidence: float = Form(default=0.25),
    iou: float = Form(default=0.45),
    enable_llm: bool = Form(default=True),
):
    if file is None and not sample_name:
        raise HTTPException(status_code=400, detail="请上传图片或选择本地图片")
    if file is not None:
        image_bytes = await file.read()
        input_name = file.filename or "uploaded-image"
    else:
        path = _safe_sample_path("image", sample_name)
        image_bytes = path.read_bytes()
        input_name = path.name
    image = _read_image_bytes(image_bytes)
    result = _detect_pil(image, confidence, iou)
    summary = {
        "input_type": "image",
        "input_name": input_name,
        "detection_count": result["detection_count"],
        "max_confidence": result["max_confidence"],
        "detections": result["detections"],
    }
    result.update(
        {
            "input_type": "image",
            "input_name": input_name,
            "analysis": _ollama_analysis(summary) if enable_llm else _rule_analysis(summary),
        }
    )
    return result


@router.post("/detect/frame")
async def detect_frame(
    file: UploadFile = File(...),
    confidence: float = Form(default=0.25),
    iou: float = Form(default=0.45),
):
    image_bytes = await file.read()
    image = _read_image_bytes(image_bytes)
    result = _detect_pil(image, confidence, iou)
    result.update({"input_type": "video_frame", "input_name": file.filename or "frame.jpg"})
    result.pop("annotated_image", None)
    return result


@router.get("/detect/video-frame/{name}")
def detect_video_frame(
    name: str,
    frame_index: int = 0,
    confidence: float = 0.25,
    iou: float = 0.45,
):
    try:
        import cv2
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OpenCV 不可用: {exc}")

    video_path = _safe_sample_path("video", name)
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise HTTPException(status_code=400, detail="视频无法打开")
    try:
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        target_index = max(0, min(int(frame_index or 0), max(0, frame_count - 1)))
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_index)
        ok, frame = cap.read()
        if not ok:
            raise HTTPException(status_code=400, detail="视频帧读取失败")
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        result = _detect_pil(pil, confidence, iou)
        return {
            **result,
            "input_type": "video_frame",
            "input_name": name,
            "frame_index": target_index,
            "frame_count": frame_count,
            "fps": round(fps, 2),
            "video_width": width,
            "video_height": height,
            "is_end": target_index >= max(0, frame_count - 1),
        }
    finally:
        cap.release()


@router.post("/analyze")
def analyze_detection(body: AnalysisBody):
    return _ollama_analysis(body.summary)


@router.get("/detect/video-stream/{name}")
def detect_video_stream(
    name: str,
    confidence: float = 0.25,
    iou: float = 0.45,
    frame_stride: int = 3,
):
    try:
        import cv2
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OpenCV 不可用: {exc}")

    video_path = _safe_sample_path("video", name)
    stride = max(1, min(int(frame_stride or 3), 12))

    def generate():
        cap = cv2.VideoCapture(str(video_path))
        frame_index = 0
        try:
            while cap.isOpened():
                ok, frame = cap.read()
                if not ok:
                    break
                if frame_index % stride != 0:
                    frame_index += 1
                    continue
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil = Image.fromarray(rgb)
                frame_result = _detect_pil(pil, confidence, iou)
                annotated_url = frame_result.get("annotated_image", "")
                if "," in annotated_url:
                    jpg_bytes = base64.b64decode(annotated_url.split(",", 1)[1])
                else:
                    buffer = io.BytesIO()
                    pil.save(buffer, format="JPEG", quality=88)
                    jpg_bytes = buffer.getvalue()
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + jpg_bytes + b"\r\n"
                )
                frame_index += 1
        finally:
            cap.release()

    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={"Cache-Control": "no-store"},
    )


@router.post("/detect/video")
async def detect_video(
    file: UploadFile | None = File(default=None),
    sample_name: str = Form(default=""),
    confidence: float = Form(default=0.25),
    iou: float = Form(default=0.45),
    max_frames: int = Form(default=6),
    enable_llm: bool = Form(default=True),
):
    try:
        import cv2
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"视频抽帧依赖 OpenCV 不可用: {exc}")

    temp_path = None
    if file is None and not sample_name:
        raise HTTPException(status_code=400, detail="请上传视频或选择本地视频")
    if file is not None:
        suffix = Path(file.filename or "upload.avi").suffix or ".avi"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp.write(await file.read())
            temp_path = Path(temp.name)
        video_path = temp_path
        input_name = file.filename or "uploaded-video"
    else:
        video_path = _safe_sample_path("video", sample_name)
        input_name = video_path.name

    started = time.perf_counter()
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        if temp_path:
            temp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="视频无法打开")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    indices = _frame_indices(frame_count, max_frames)
    key_frames = []
    total_detections = 0
    max_conf = 0.0
    for frame_index in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        frame_result = _detect_pil(pil, confidence, iou)
        total_detections += frame_result["detection_count"]
        max_conf = max(max_conf, frame_result["max_confidence"])
        key_frames.append(
            {
                "frame_index": frame_index,
                "time_sec": round(frame_index / fps, 2) if fps else None,
                "detection_count": frame_result["detection_count"],
                "max_confidence": frame_result["max_confidence"],
                "annotated_image": frame_result["annotated_image"],
                "detections": frame_result["detections"],
            }
        )
    cap.release()
    if temp_path:
        temp_path.unlink(missing_ok=True)

    summary = {
        "input_type": "video",
        "input_name": input_name,
        "sampled_frames": len(key_frames),
        "total_detections": total_detections,
        "max_confidence": round(max_conf, 4),
    }
    return {
        "input_type": "video",
        "input_name": input_name,
        "frame_count": frame_count,
        "fps": round(fps, 2),
        "video_width": width,
        "video_height": height,
        "sampled_frames": len(key_frames),
        "key_frames": key_frames,
        "detection_count": total_detections,
        "max_confidence": round(max_conf, 4),
        "runtime_sec": round(time.perf_counter() - started, 4),
        "analysis": _ollama_analysis(summary) if enable_llm else _rule_analysis(summary),
    }


def _frame_indices(frame_count: int, max_frames: int) -> list[int]:
    if frame_count <= 0:
        return [0]
    count = max(1, min(max_frames, 12, frame_count))
    if count == 1:
        return [frame_count // 2]
    return sorted({round(i * (frame_count - 1) / (count - 1)) for i in range(count)})
