import authApi from './auth_api';

export const createWorkspace = async (workspaceData) => {
  const response = await authApi.post('/workspaces/', workspaceData);

  return response.data;
};

export const getWorkspaces = async () => {
  const response = await authApi.get('/workspaces/');

  return response.data;
};

export const updateWorkspace = async (workspaceId, workspaceData) => {
  const response = await authApi.patch(
    `/workspaces/${workspaceId}`,
    workspaceData,
  );

  return response.data;
};

export const deleteWorkspace = async (workspaceId) => {
  const response = await authApi.delete(`/workspaces/${workspaceId}`);

  return response.data;
};
