// ============================================================
// INSIGHT API
// ============================================================

import authApi from './auth_api';

// ============================================================
// GET DATASET INSIGHTS
// ============================================================

export const getDatasetInsights = async (datasetId, projectId, workspaceId) => {
  const response = await authApi.get(`/insights/dataset/${datasetId}`, {
    params: {
      project_id: projectId,
      workspace_id: workspaceId,
    },
  });

  return response.data;
};
