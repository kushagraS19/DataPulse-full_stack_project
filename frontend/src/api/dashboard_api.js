import authApi from './auth_api';

// ============================================================
// DASHBOARD GENERATION
// ============================================================

export const generateDashboard = async ({
  dashboardId,
  datasetId,
  projectId,
  workspaceId,
}) => {
  const response = await authApi.get(`/dashboards/${dashboardId}/generate`, {
    params: {
      dataset_id: datasetId,
      project_id: projectId,
      workspace_id: workspaceId,
    },
  });

  return response.data;
};

// ============================================================
// CHART DATA
// ============================================================

export const getChartData = async ({
  chartId,
  dashboardId,
  projectId,
  workspaceId,
}) => {
  const response = await authApi.get(`/charts/${chartId}/data`, {
    params: {
      dashboard_id: dashboardId,
      project_id: projectId,
      workspace_id: workspaceId,
    },
  });

  return response.data;
};

// ============================================================
// CHART KPI
// ============================================================

export const getChartKpi = async ({
  chartId,
  dashboardId,
  projectId,
  workspaceId,
}) => {
  const response = await authApi.get(`/charts/${chartId}/kpi`, {
    params: {
      dashboard_id: dashboardId,
      project_id: projectId,
      workspace_id: workspaceId,
    },
  });

  return response.data;
};
