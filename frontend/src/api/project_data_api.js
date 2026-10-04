import authApi from './auth_api';

export const getProjectDashboards = async (projectId, workspaceId) => {
  const response = await authApi.get(`/dashboards/project/${projectId}`, {
    params: {
      workspace_id: workspaceId,
    },
  });

  return response.data;
};

export const getProjectDatasets = async (projectId, workspaceId) => {
  const response = await authApi.get(`/datasets/project/${projectId}`, {
    params: {
      workspace_id: workspaceId,
    },
  });

  return response.data;
};
