import request from "./request";
export const getModalities = () => request.get("/data/modalities");
export const getRecords = (params) => request.get("/data/records", { params });
export const getRecord = (id, source) =>
  request.get(`/data/records/${id}`, { params: { source } });
