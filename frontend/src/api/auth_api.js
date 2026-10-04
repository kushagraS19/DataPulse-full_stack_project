import axios from 'axios';

const API_URL = 'http://localhost:8000';

const authApi = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

let refreshPromise = null;

// Attach the current access token to normal API requests
authApi.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem('access_token');

    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    return config;
  },
  (error) => Promise.reject(error),
);

// Handle expired access tokens
authApi.interceptors.response.use(
  (response) => response,

  async (error) => {
    const originalRequest = error.config;

    if (!originalRequest) {
      return Promise.reject(error);
    }

    const requestUrl = originalRequest.url || '';

    const isRefreshRequest = requestUrl.includes('/auth/refresh');
    const isLoginRequest = requestUrl.includes('/auth/login');

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !isRefreshRequest &&
      !isLoginRequest
    ) {
      originalRequest._retry = true;

      try {
        /*
         * Use plain axios here instead of authApi.
         *
         * This prevents the refresh request from passing
         * through the same response interceptor again.
         */
        if (!refreshPromise) {
          refreshPromise = axios
            .post(
              `${API_URL}/auth/refresh`,
              {},
              {
                withCredentials: true,
                headers: {
                  'Content-Type': 'application/json',
                },
              },
            )
            .then((response) => {
              const newAccessToken = response.data.access_token;

              if (!newAccessToken) {
                throw new Error('Access token was not returned');
              }

              localStorage.setItem('access_token', newAccessToken);

              return newAccessToken;
            })
            .finally(() => {
              refreshPromise = null;
            });
        }

        const newAccessToken = await refreshPromise;

        originalRequest.headers = {
          ...originalRequest.headers,
          Authorization: `Bearer ${newAccessToken}`,
        };

        return authApi(originalRequest);
      } catch (refreshError) {
        console.log(
          'REFRESH ERROR:',
          refreshError.response?.status,
          refreshError.response?.data,
        );

        refreshPromise = null;

        localStorage.removeItem('access_token');

        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  },
);

export default authApi;
