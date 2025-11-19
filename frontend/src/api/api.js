import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api';

export const sendMessage = async (text) => {
  const message = JSON.stringify({ message: text });
  const res = await axios.post(`${API_URL}/chat`, { message });

  return res.data;
};

export const uploadPdf = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const res = await axios.post(`${API_URL}/upload_file`, formData, {
    onUploadProgress: (e) => {
      const percent = Math.round((e.loaded * 100) / e.total);
      if (onProgress) onProgress(percent);
    },
  });

  return res.data;
};
