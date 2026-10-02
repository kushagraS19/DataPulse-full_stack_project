import { useEffect, useState } from 'react';

import { generateDashboard, getChartData } from '../api/dashboard_api';

import ChartCard from '../components/dashboard/ChartCard';
import ChartRenderer from '../components/dashboard/ChartRenderer';

function Dashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [chartData, setChartData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const dashboardId = 1;
  const datasetId = 12;
  const projectId = 1;
  const workspaceId = 1;

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        setLoading(true);
        setError(null);

        const token = localStorage.getItem('access_token');

        if (!token) {
          throw new Error('Authentication token not found');
        }

        // Generate dashboard configuration

        const dashboardResponse = await generateDashboard({
          dashboardId,
          datasetId,
          projectId,
          workspaceId,
          token,
        });

        setDashboard(dashboardResponse);

        // Fetch data for every chart

        const chartResponses = await Promise.all(
          dashboardResponse.charts.map(async (chart) => {
            const response = await getChartData({
              chartId: chart.id,
              dashboardId,
              projectId,
              workspaceId,
              token,
            });

            return {
              chartId: chart.id,
              data: response.data || [],
            };
          }),
        );

        // Convert responses into:

        // {
        //     47: [...],
        //     48: [...],
        //     49: [...]
        // }

        const chartDataMap = chartResponses.reduce((accumulator, chart) => {
          accumulator[chart.chartId] = chart.data;

          return accumulator;
        }, {});

        setChartData(chartDataMap);
      } catch (error) {
        console.error('Dashboard loading failed:', error);

        setError(
          error.response?.data?.detail ||
            error.message ||
            'Failed to load dashboard',
        );
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className='flex min-h-screen items-center justify-center bg-slate-50 dark:bg-slate-950'>
        <div className='text-center'>
          <div className='mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-indigo-600' />

          <h2 className='text-lg font-semibold text-slate-900 dark:text-white'>
            Building your dashboard
          </h2>

          <p className='mt-1 text-sm text-slate-500'>
            DataPulse is analyzing your dataset...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className='flex min-h-screen items-center justify-center bg-slate-50 p-6 dark:bg-slate-950'>
        <div className='w-full max-w-md rounded-2xl border border-red-200 bg-white p-6 shadow-lg dark:border-red-900 dark:bg-slate-900'>
          <h2 className='text-lg font-semibold text-red-600'>
            Dashboard Error
          </h2>

          <p className='mt-2 text-sm text-slate-600 dark:text-slate-300'>
            {error}
          </p>
        </div>
      </div>
    );
  }

  if (!dashboard) {
    return null;
  }

  return (
    <div className='min-h-screen bg-slate-50 px-4 py-6 text-slate-900 dark:bg-slate-950 dark:text-white sm:px-6 lg:px-8'>
      <div className='mx-auto max-w-7xl'>
        {/* Header */}

        <header className='mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between'>
          <div>
            <p className='text-sm font-medium text-indigo-600'>
              DataPulse Analytics
            </p>

            <h1 className='mt-1 text-3xl font-bold tracking-tight'>
              Your Dashboard
            </h1>

            <p className='mt-2 text-sm text-slate-500 dark:text-slate-400'>
              Automatically generated from your dataset
            </p>
          </div>

          <button
            type='button'
            onClick={() => window.location.reload()}
            className='rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200'
          >
            ↻ Refresh
          </button>
        </header>

        {/* KPI Section */}

        {dashboard.kpis?.length > 0 && (
          <section className='mb-8'>
            <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
              {dashboard.kpis.map((kpi, index) => (
                <div
                  key={kpi.name || `kpi-${index}`}
                  className='group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl dark:border-slate-800 dark:bg-slate-900'
                >
                  <p className='text-sm font-medium text-slate-500 dark:text-slate-400'>
                    {kpi.name}
                  </p>

                  <p className='mt-3 text-2xl font-bold tracking-tight'>
                    {kpi.value ?? '-'}
                  </p>

                  {kpi.operation && (
                    <p className='mt-2 text-xs capitalize text-slate-400'>
                      {kpi.operation}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Charts */}

        <section>
          <div className='mb-4 flex items-center justify-between'>
            <div>
              <h2 className='text-xl font-semibold'>Analytics</h2>

              <p className='mt-1 text-sm text-slate-500 dark:text-slate-400'>
                Insights generated from your data
              </p>
            </div>

            <span className='rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300'>
              {dashboard.charts?.length || 0} charts
            </span>
          </div>

          <div className='grid gap-6 lg:grid-cols-2'>
            {dashboard.charts?.map((chart, index) => (
              <ChartCard
                key={chart.id || `chart-${index}`}
                title={chart.name}
                chartType={chart.chart_type}
                onExpand={() => {
                  console.log('Expand chart:', chart);
                }}
              >
                <ChartRenderer chart={chart} data={chartData[chart.id] || []} />
              </ChartCard>
            ))}
          </div>
        </section>

        {/* Insights */}

        {dashboard.insights?.length > 0 && (
          <section className='mt-8'>
            <h2 className='mb-4 text-xl font-semibold'>Insights</h2>

            <div className='grid gap-4 md:grid-cols-2'>
              {dashboard.insights.map((insight, index) => (
                <div
                  key={index}
                  className='rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900'
                >
                  <p className='text-sm leading-6 text-slate-600 dark:text-slate-300'>
                    {typeof insight === 'string'
                      ? insight
                      : insight.message ||
                        insight.text ||
                        JSON.stringify(insight)}
                  </p>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
