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

        const dashboardResponse = await generateDashboard({
          dashboardId,
          datasetId,
          projectId,
          workspaceId,
          token,
        });

        setDashboard(dashboardResponse);

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
      <div className='flex min-h-screen items-center justify-center bg-stone-50'>
        <div className='text-center'>
          <div className='mx-auto mb-4 h-9 w-9 animate-spin rounded-full border-4 border-stone-200 border-t-slate-700' />

          <h2 className='text-lg font-semibold text-slate-900'>
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
      <div className='flex min-h-screen items-center justify-center bg-stone-50 p-6'>
        <div className='w-full max-w-md rounded-2xl border border-red-200 bg-white p-6 shadow-sm'>
          <h2 className='text-lg font-semibold text-red-600'>
            Dashboard Error
          </h2>

          <p className='mt-2 text-sm text-slate-600'>{error}</p>
        </div>
      </div>
    );
  }

  if (!dashboard) {
    return null;
  }

  const kpiStyles = [
    {
      accent: 'bg-amber-500',
      dot: 'bg-amber-500',
      value: 'text-amber-700',
      badge: 'bg-amber-50 text-amber-700 border-amber-100',
    },
    {
      accent: 'bg-blue-500',
      dot: 'bg-blue-500',
      value: 'text-blue-700',
      badge: 'bg-blue-50 text-blue-700 border-blue-100',
    },
    {
      accent: 'bg-rose-500',
      dot: 'bg-rose-500',
      value: 'text-rose-700',
      badge: 'bg-rose-50 text-rose-700 border-rose-100',
    },
    {
      accent: 'bg-teal-500',
      dot: 'bg-teal-500',
      value: 'text-teal-700',
      badge: 'bg-teal-50 text-teal-700 border-teal-100',
    },
  ];

  return (
    <div className='min-h-screen bg-stone-50 px-4 py-6 text-slate-900 sm:px-6 lg:px-8'>
      <div className='mx-auto max-w-7xl'>
        {/* Header */}

        <header className='relative mb-10 overflow-hidden rounded-3xl border border-stone-200 bg-white px-6 py-7 shadow-sm sm:px-8 sm:py-8'>
          <div className='pointer-events-none absolute -right-20 -top-24 h-64 w-64 rounded-full bg-slate-100 opacity-70 blur-3xl' />

          <div className='pointer-events-none absolute -bottom-24 left-1/3 h-48 w-48 rounded-full bg-stone-100 opacity-70 blur-3xl' />

          <div className='relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between'>
            <div className='min-w-0'>
              <div className='mb-3 flex items-center gap-2'>
                <span className='h-2 w-2 rounded-full bg-emerald-500 shadow-sm shadow-emerald-200' />

                <p className='text-xs font-semibold uppercase tracking-[0.18em] text-slate-500'>
                  DataPulse Analytics
                </p>
              </div>

              <h1 className='text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl'>
                Your Dashboard
              </h1>

              <p className='mt-3 max-w-2xl text-sm leading-6 text-slate-500 sm:text-base'>
                Automatically generated insights and visualizations from your
                dataset.
              </p>

              <div className='mt-5 flex flex-wrap items-center gap-3'>
                <div className='inline-flex items-center gap-2 rounded-full border border-stone-200 bg-stone-50 px-3 py-1.5'>
                  <span className='h-1.5 w-1.5 rounded-full bg-emerald-500' />

                  <span className='text-xs font-medium text-slate-600'>
                    Analysis ready
                  </span>
                </div>

                <div className='inline-flex items-center rounded-full border border-stone-200 bg-white px-3 py-1.5'>
                  <span className='text-xs font-medium text-slate-500'>
                    {dashboard.charts?.length || 0} visualizations
                  </span>
                </div>
              </div>
            </div>

            <div className='flex flex-wrap items-center gap-3'>
              <button
                type='button'
                onClick={() => {
                  console.log('Export dashboard');
                }}
                className='group inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:bg-slate-800 hover:shadow-md active:translate-y-0'
              >
                <span className='text-base transition-transform duration-300 group-hover:translate-y-0.5'>
                  ↓
                </span>

                <span>Export</span>
              </button>

              <button
                type='button'
                onClick={() => window.location.reload()}
                className='group inline-flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:border-slate-300 hover:bg-slate-50 hover:shadow-md active:translate-y-0'
              >
                <span className='text-base transition-transform duration-500 group-hover:rotate-180'>
                  ↻
                </span>

                <span>Refresh</span>
              </button>
            </div>
          </div>
        </header>

        {/* KPI Section */}

        {dashboard.kpis?.length > 0 && (
          <section className='mb-10'>
            <div className='mb-4 flex items-end justify-between'>
              <div>
                <h2 className='text-xl font-semibold tracking-tight text-slate-900'>
                  Key Metrics
                </h2>

                <p className='mt-1 text-sm text-slate-500'>
                  A quick overview of your dataset
                </p>
              </div>
            </div>

            <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
              {dashboard.kpis.map((kpi, index) => {
                const style = kpiStyles[index % kpiStyles.length];

                return (
                  <div
                    key={kpi.name || `kpi-${index}`}
                    className='group relative overflow-hidden rounded-2xl border border-stone-200 bg-white p-5 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-slate-300 hover:shadow-lg'
                  >
                    {/* Accent */}

                    <div
                      className={`absolute left-0 top-0 h-full w-1 ${style.accent} opacity-80 transition-all duration-300 group-hover:w-1.5`}
                    />

                    <div className='pl-2'>
                      <div className='flex items-start justify-between gap-3'>
                        <div className='min-w-0'>
                          <p className='truncate text-xs font-semibold uppercase tracking-[0.12em] text-slate-400'>
                            {kpi.name}
                          </p>
                        </div>

                        <span
                          className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${style.dot} opacity-80`}
                        />
                      </div>

                      <p
                        className={`mt-4 text-3xl font-bold tracking-tight ${style.value}`}
                      >
                        {kpi.value ?? '-'}
                      </p>

                      {kpi.operation && (
                        <div className='mt-4'>
                          <span
                            className={`inline-flex rounded-md border px-2 py-1 text-[10px] font-semibold uppercase tracking-wider ${style.badge}`}
                          >
                            {kpi.operation}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* Charts */}

        <section>
          <div className='mb-5 flex items-center justify-between'>
            <div>
              <h2 className='text-xl font-semibold tracking-tight text-slate-900'>
                Analytics
              </h2>

              <p className='mt-1 text-sm text-slate-500'>
                Insights generated from your data
              </p>
            </div>

            <span className='rounded-full border border-stone-200 bg-white px-3 py-1 text-xs font-medium text-slate-500'>
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
          <section className='mt-10'>
            <div className='mb-5'>
              <h2 className='text-xl font-semibold tracking-tight text-slate-900'>
                Insights
              </h2>

              <p className='mt-1 text-sm text-slate-500'>
                Observations generated from your dataset
              </p>
            </div>

            <div className='grid gap-4 md:grid-cols-2'>
              {dashboard.insights.map((insight, index) => (
                <div
                  key={index}
                  className='group rounded-2xl border border-stone-200 bg-white p-5 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md'
                >
                  <div className='flex gap-4'>
                    <div className='mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-xs font-semibold text-slate-600'>
                      {index + 1}
                    </div>

                    <p className='text-sm leading-6 text-slate-600'>
                      {typeof insight === 'string'
                        ? insight
                        : insight.message ||
                          insight.text ||
                          JSON.stringify(insight)}
                    </p>
                  </div>
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
