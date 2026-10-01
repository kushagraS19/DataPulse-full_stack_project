import authApi from './auth_api';

export const createChart = async (chartData) => {
  const response = await authApi.post('/charts/', chartData);

  return response.data;
};

export const getChartData = async (
  chartId,
  dashboardId,
  projectId,
  workspaceId,
) => {
  const response = await authApi.get(`/charts/${chartId}/data`, {
    params: {
      dashboard_id: dashboardId,
      project_id: projectId,
      workspace_id: workspaceId,
    },
  });

  return response.data;
};
