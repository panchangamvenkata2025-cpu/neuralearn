import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000/api"
});

export const useRAG = () => {
  const askQuestion = async (data) => {
    const res = await API.post("/chat/", data);
    return res.data;
  };

  const uploadFile = async (formData) => {
    const res = await API.post("/upload/", formData);
    return res.data;
  };

  return { askQuestion, uploadFile };
};