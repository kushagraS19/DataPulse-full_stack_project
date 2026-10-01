import authApi from './auth_api';

export const getDatasetColumns = async (datasetId, projectId, workspaceId) => {
  const response = await authApi.get(`/datasets/${datasetId}/columns`, {
    params: {
      project_id: projectId,
      workspace_id: workspaceId,
    },
  });

  return response.data;
};

export const getDatasetColumnOperations = async (
  datasetId,
  projectId,
  workspaceId,
) => {
  const response = await authApi.get(
    `/datasets/${datasetId}/column-operations`,
    {
      params: {
        project_id: projectId,
        workspace_id: workspaceId,
      },
    },
  );

  return response.data;
};
