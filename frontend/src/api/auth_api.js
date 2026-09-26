import axios from 'axios';

const authApi = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add access token to every request
authApi.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem('access_token');

    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// Handle expired access tokens
authApi.interceptors.response.use(
  (response) => {
    return response;
  },

  async (error) => {
    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url.includes('/auth/refresh')
    ) {
      originalRequest._retry = true;

      try {
        const response = await axios.post(
          'http://127.0.0.1:8000/auth/refresh',
          {},
          {
            withCredentials: true,
          },
        );

        const newAccessToken = response.data.access_token;

        localStorage.setItem('access_token', newAccessToken);

        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

        return authApi(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');

        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  },
);

export default authApi;
