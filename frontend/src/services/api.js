import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const sendCommand = async (text) => {
  const response = await API.post("/api/chat", {
    text,
    user_id: "zain",
  });

  return response.data;
};