import axios from 'axios';

const API_URL = 'https://your-render-app.onrender.com/api'; // Replace with your actual API URL

const apiClient = axios.create({
  baseURL: API_URL,
  responseType: 'json',
  headers: {
    'Content-Type': 'application/json'
  }
});

export const getScholarships = () => {
  return apiClient.get('/scholarships');
};

export const getFaqs = () => {
  return apiClient.get('/faqs');
};
