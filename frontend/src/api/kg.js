import request from "./request";
export const getGraph = (params) => request.get("/kg/graph", { params });
export const getNode = (id) => request.get(`/kg/node/${id}`);
export const getNeighbors = (id) => request.get(`/kg/neighbors/${id}`);
