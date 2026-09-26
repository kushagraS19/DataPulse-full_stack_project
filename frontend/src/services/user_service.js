import authApi from '../api/auth_api';

export const getCurrentUser = async () => {
  const response = await authApi.get('/users/me');

  return response.data;
};
