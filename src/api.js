import axios from "axios";
import { LANGUAGE_VERSIONS } from "./constants";

const API = axios.create({
  baseURL: "https://emkc.org/api/v2/piston",
});

const BACKEND_API = axios.create({
  baseURL: "http://localhost:8000", // Your backend URL
});

export const executeCode = async (language, sourceCode) => {
  const response = await API.post("/execute", {
    language: language,
    version: LANGUAGE_VERSIONS[language],
    files: [
      {
        content: sourceCode,
      },
    ],
  });
  return response.data;
};


export const sendCodeToBackend = async (frontendLanguage, frontendCode,task) => {
  try {
    const response = await BACKEND_API.post("/process-code", {
      frontend_language: frontendLanguage,
      frontend_code: frontendCode,
      task:task,
    });
    return response.data;
  } catch (error) {
    console.error("Error sending code to backend:", error);
    throw error;
  }
};