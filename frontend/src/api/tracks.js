import request from "./request";
export const getTracks = (params) => request.get("/tracks", { params });
export const getTrack = (id) => request.get(`/tracks/${id}`);
export const getTrackFeatures = (id) => request.get(`/tracks/${id}/features`);
