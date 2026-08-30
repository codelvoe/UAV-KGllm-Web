import request from "./request";
export const getSummary = () => request.get("/dashboard/summary");
export const getCharts = () => request.get("/dashboard/charts");
