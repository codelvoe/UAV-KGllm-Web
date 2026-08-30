import request from "./request";
export const getDetection = () => request.get("/experiments/detection");
export const getEfficiency = () => request.get("/experiments/efficiency");
export const getRobustness = () => request.get("/experiments/robustness");
