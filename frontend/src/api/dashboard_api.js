import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

export const generateDashboard = async ({
  dashboardId,
  datasetId,
  projectId,
  workspaceId,
  token,
}) => {
  const response = await axios.get(
    `${API_URL}/dashboards/${dashboardId}/generate`,
    {
      params: {
        dataset_id: datasetId,
        project_id: projectId,
        workspace_id: workspaceId,
      },
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  return response.data;
};
