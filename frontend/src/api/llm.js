import request from "./request";
export const makeDecision = (data) => request.post("/llm/decision", data);
