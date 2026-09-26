import authApi from '../api/auth_api';

export const registerUser = async (userData) => {
  const response = await authApi.post('/users/register', userData);

  return response.data;
};

export const loginUser = async (loginData) => {
  const response = await authApi.post('/auth/login', loginData);

  return response.data;
};

export const refreshAccessToken = async () => {
  const response = await authApi.post('/auth/refresh');

  return response.data;
};

export const logoutUser = async () => {
  const response = await authApi.post('/auth/logout');

  return response.data;
};
