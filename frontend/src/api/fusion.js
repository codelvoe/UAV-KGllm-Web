import request from "./request";
export const getCandidates = (params) =>
  request.get("/fusion/candidates", { params });
export const getCandidate = (id) => request.get(`/fusion/candidates/${id}`);
export const getScoreBreakdown = (id) =>
  request.get(`/fusion/score-breakdown/${id}`);
