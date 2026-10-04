import authApi from './auth_api';

export const createProject = async (projectData) => {
  const response = await authApi.post('/projects/', projectData);

  return response.data;
};

export const getWorkspaceProjects = async (workspaceId) => {
  const response = await authApi.get(`/projects/workspace/${workspaceId}`);

  return response.data;
};

export const getProject = async (projectId, workspaceId) => {
  const response = await authApi.get(`/projects/${projectId}`, {
    params: {
      workspace_id: workspaceId,
    },
  });

  return response.data;
};

export const updateProject = async (projectId, projectData) => {
  const response = await authApi.patch(`/projects/${projectId}`, projectData);

  return response.data;
};

export const deleteProject = async (projectId) => {
  const response = await authApi.delete(`/projects/${projectId}`);

  return response.data;
};
