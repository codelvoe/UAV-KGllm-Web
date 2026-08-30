import request from "./request";
export const sendMessage = (data) => request.post("/chat/send", data);
export const getSessions = () => request.get("/chat/sessions");
export const newSession = () => request.post("/chat/new");
export const deleteSession = (id) => request.delete(`/chat/sessions/${id}`);
export const getOllamaStatus = () => request.get("/chat/ollama-status");
