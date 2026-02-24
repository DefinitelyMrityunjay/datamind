import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
});

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const res = await API.post("/upload", formData);
  return res.data;
};

export const getDashboard = async (tableName) => {
  const res = await API.get(`/dashboard/${tableName}`);
  return res.data;
};