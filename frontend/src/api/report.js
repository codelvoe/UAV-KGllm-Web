import request from "./request";
export const addReportItem = (data) => request.post("/report/add-item", data);
export const getDraft = () => request.get("/report/draft");
export const generateReport = () => request.post("/report/generate");
export const clearReport = () => request.delete("/report/clear");
