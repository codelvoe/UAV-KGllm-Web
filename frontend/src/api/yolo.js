import request from "./request";

export const getYoloStatus = () => request.get("/yolo/status");
export const getYoloSamples = () => request.get("/yolo/samples");

export const detectYoloImage = (formData) =>
  request.post("/yolo/detect/image", formData, {
    timeout: 180000,
    headers: { "Content-Type": "multipart/form-data" },
  });

export const detectYoloVideo = (formData) =>
  request.post("/yolo/detect/video", formData, {
    timeout: 240000,
    headers: { "Content-Type": "multipart/form-data" },
  });

export const detectYoloFrame = (formData) =>
  request.post("/yolo/detect/frame", formData, {
    timeout: 60000,
    headers: { "Content-Type": "multipart/form-data" },
  });

export const detectYoloVideoFrame = (name, params) =>
  request.get(`/yolo/detect/video-frame/${encodeURIComponent(name)}`, {
    params,
    timeout: 60000,
  });

export const analyzeYoloDetection = (summary) =>
  request.post("/yolo/analyze", { summary }, { timeout: 120000 });
