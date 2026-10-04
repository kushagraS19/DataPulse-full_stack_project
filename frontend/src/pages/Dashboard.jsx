import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { generateDashboard, getChartData } from '../api/dashboard_api';

import {
  getProjectDashboards,
  getProjectDatasets,
} from '../api/project_data_api';

import ChartCard from '../components/dashboard/ChartCard';
import ChartRenderer from '../components/dashboard/ChartRenderer';

function Dashboard({ project, workspace }) {
  const navigate = useNavigate();

  const [dashboard, setDashboard] = useState(null);
  const [chartData, setChartData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedChart, setExpandedChart] = useState(null);
  const [retryToken, setRetryToken] = useState(0);

  const loadedProjectRef = useRef(null);
  const activeLoadKeyRef = useRef(null);

  useEffect(() => {
    if (!expandedChart) {
      return undefined;
    }

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        setExpandedChart(null);
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [expandedChart]);

  useEffect(() => {
    if (!project || !workspace) {
      return;
    }

    if (retryToken > 0) {
      loadedProjectRef.current = null;
    }

    const projectId = project.id;
    const workspaceId = workspace.id;
    const loadKey = `${projectId}:${workspaceId}`;

    // React StrictMode can run effects twice in development.
    // Dashboard generation recreates chart records, so allowing two
    // generations at the same time can leave the first response holding
    // chart IDs that the second generation has already replaced.
    if (loadedProjectRef.current === loadKey) {
      return;
    }

    loadedProjectRef.current = loadKey;
    activeLoadKeyRef.current = loadKey;

    const loadDashboard = async () => {
      try {
        setLoading(true);
        setError(null);
        setDashboard(null);
        setChartData({});

        const dashboards = await getProjectDashboards(projectId, workspaceId);

        if (!dashboards || dashboards.length === 0) {
          throw new Error('No dashboard found for this project');
        }

        const datasets = await getProjectDatasets(projectId, workspaceId);

        if (!datasets || datasets.length === 0) {
          throw new Error('No dataset found for this project');
        }

        const selectedDashboard = dashboards[0];
        const selectedDataset = datasets[0];

        const dashboardId = selectedDashboard.id;
        const datasetId = selectedDataset.id;

        const dashboardResponse = await generateDashboard({
          dashboardId,
          datasetId,
          projectId,
          workspaceId,
        });

        if (activeLoadKeyRef.current !== loadKey) {
          return;
        }

        // KPIs are calculated by the dashboard generator. They are not
        // related to individual chart IDs.
        setDashboard(dashboardResponse);

        const charts = dashboardResponse.charts || [];

        // One broken/stale chart must not make the entire dashboard fail.
        // This is especially important while charts are being regenerated.
        const chartResponses = await Promise.all(
          charts.map(async (chart) => {
            try {
              const response = await getChartData({
                chartId: chart.id,
                dashboardId,
                projectId,
                workspaceId,
              });

              return {
                chartId: chart.id,
                data: response.data || [],
              };
            } catch (chartError) {
              console.warn(`Failed to load chart ${chart.id}:`, chartError);

              return null;
            }
          }),
        );

        if (activeLoadKeyRef.current !== loadKey) {
          return;
        }

        const chartDataMap = chartResponses.reduce((accumulator, chart) => {
          if (chart) {
            accumulator[chart.chartId] = chart.data;
          }

          return accumulator;
        }, {});

        setChartData(chartDataMap);
      } catch (error) {
        if (activeLoadKeyRef.current !== loadKey) {
          return;
        }

        console.error('Dashboard loading failed:', error);

        setError(
          error.response?.data?.detail ||
            error.message ||
            'Failed to load dashboard',
        );
      } finally {
        if (activeLoadKeyRef.current === loadKey) {
          setLoading(false);
        }
      }
    };

    loadDashboard();
  }, [project?.id, workspace?.id, retryToken]);

  if (loading) {
    return (
      <div className='datapulse-dashboard min-h-screen bg-stone-50 px-4 py-6 sm:px-6 lg:px-8'>
        <div className='datapulse-dashboard-inner mx-auto max-w-7xl'>
          <div className='mb-10 overflow-hidden rounded-3xl border border-stone-200 bg-white p-6 shadow-sm sm:p-8'>
            <div className='animate-pulse'>
              <div className='mb-4 h-3 w-36 rounded-full bg-stone-200' />
              <div className='h-9 w-2/3 max-w-md rounded-xl bg-stone-200' />
              <div className='mt-4 h-4 w-full max-w-2xl rounded-full bg-stone-100' />
              <div className='mt-2 h-4 w-3/4 max-w-xl rounded-full bg-stone-100' />
              <div className='mt-6 flex flex-wrap gap-3'>
                <div className='h-8 w-28 rounded-full bg-stone-100' />
                <div className='h-8 w-32 rounded-full bg-stone-100' />
              </div>
            </div>
          </div>
          <div className='mb-10'>
            <div className='mb-5'>
              <div className='h-6 w-32 animate-pulse rounded-lg bg-stone-200' />
              <div className='mt-2 h-4 w-52 animate-pulse rounded-full bg-stone-100' />
            </div>
            <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
              {[0, 1, 2, 3].map((item) => (
                <div
                  key={item}
                  className='h-36 animate-pulse rounded-2xl border border-stone-200 bg-white p-5 shadow-sm'
                >
                  <div className='h-3 w-24 rounded-full bg-stone-100' />
                  <div className='mt-6 h-9 w-28 rounded-xl bg-stone-200' />
                  <div className='mt-5 h-6 w-16 rounded-md bg-stone-100' />
                </div>
              ))}
            </div>
          </div>
          <div>
            <div className='mb-5'>
              <div className='h-6 w-28 animate-pulse rounded-lg bg-stone-200' />
              <div className='mt-2 h-4 w-56 animate-pulse rounded-full bg-stone-100' />
            </div>
            <div className='grid gap-6 lg:grid-cols-2'>
              {[0, 1, 2, 3].map((item) => (
                <div
                  key={item}
                  className='h-80 animate-pulse rounded-2xl border border-stone-200 bg-white p-5 shadow-sm'
                >
                  <div className='h-5 w-40 rounded-lg bg-stone-200' />
                  <div className='mt-3 h-3 w-24 rounded-full bg-stone-100' />
                  <div className='mt-10 h-52 rounded-xl bg-stone-50' />
                </div>
              ))}
            </div>
          </div>
          <div className='mt-10 flex items-center justify-center gap-3 text-sm text-slate-500'>
            <span className='h-2 w-2 animate-pulse rounded-full bg-emerald-500' />
            <span>DataPulse is analyzing your dataset...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className='flex min-h-screen items-center justify-center bg-stone-50 px-4 py-8 sm:px-6'>
        <div className='w-full max-w-lg overflow-hidden rounded-3xl border border-stone-200 bg-white shadow-xl shadow-slate-900/5'>
          <div className='h-1.5 bg-gradient-to-r from-rose-400 via-orange-400 to-amber-400' />
          <div className='p-7 sm:p-9'>
            <div className='flex h-12 w-12 items-center justify-center rounded-2xl bg-rose-50 text-xl text-rose-600'>
              !
            </div>
            <p className='mt-5 text-xs font-semibold uppercase tracking-[0.16em] text-slate-400'>
              DataPulse Analytics
            </p>
            <h2 className='mt-2 text-2xl font-bold tracking-tight text-slate-950'>
              We couldn't build this dashboard
            </h2>
            <p className='mt-3 text-sm leading-6 text-slate-500'>
              Something went wrong while loading your project analytics. Your
              dataset is safe. You can retry the analysis or return to your
              workspaces.
            </p>
            <div className='mt-5 rounded-2xl border border-rose-100 bg-rose-50/60 p-4'>
              <p className='text-xs font-semibold uppercase tracking-wider text-rose-500'>
                Details
              </p>
              <p className='mt-1 break-words text-sm leading-6 text-rose-700'>
                {error}
              </p>
            </div>
            <div className='mt-7 flex flex-wrap gap-3'>
              <button
                type='button'
                onClick={() => {
                  setError(null);
                  setLoading(true);
                  setRetryToken((value) => value + 1);
                }}
                className='rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:bg-slate-800 hover:shadow-md active:translate-y-0'
              >
                Try again
              </button>
              <button
                type='button'
                onClick={() => navigate('/workspace')}
                className='rounded-xl border border-stone-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 transition-all duration-300 hover:-translate-y-0.5 hover:border-slate-300 hover:bg-slate-50 hover:shadow-sm active:translate-y-0'
              >
                Back to Workspaces
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className='flex min-h-screen items-center justify-center bg-stone-50 px-6'>
        <div className='max-w-md text-center'>
          <div className='mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-2xl text-slate-500'>
            ∅
          </div>
          <h2 className='mt-5 text-xl font-semibold tracking-tight text-slate-900'>
            No dashboard available
          </h2>
          <p className='mt-2 text-sm leading-6 text-slate-500'>
            There isn't enough project data to display analytics yet.
          </p>
        </div>
      </div>
    );
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
    <>
      <style>{`
        @media print {
          @page {
            size: A4;
            margin: 14mm;
          }

          body {
            background: #ffffff !important;
          }

          .datapulse-dashboard {
            min-height: auto !important;
            background: #ffffff !important;
            padding: 0 !important;
          }

          .datapulse-dashboard-inner {
            max-width: none !important;
          }

          .datapulse-export-button,
          .datapulse-refresh-button {
            display: none !important;
          }

          .datapulse-print-header {
            margin-bottom: 18px !important;
            border: 1px solid #e5e7eb !important;
            box-shadow: none !important;
            break-inside: avoid;
          }

          .datapulse-chart-grid {
            grid-template-columns: 1fr !important;
          }

          .datapulse-chart-card,
          .datapulse-insight-card {
            break-inside: avoid;
            box-shadow: none !important;
          }

          .datapulse-print-footer {
            display: block !important;
          }
        }

        .datapulse-print-footer {
          display: none;
        }

        .datapulse-chart-modal {
          animation: datapulse-modal-in 220ms cubic-bezier(0.22, 1, 0.36, 1);
        }

        .datapulse-chart-modal-panel {
          animation: datapulse-modal-panel-in 300ms cubic-bezier(0.22, 1, 0.36, 1);
        }

        .datapulse-expanded-chart > div {
          height: min(68vh, 720px) !important;
          min-height: 420px;
        }

        @keyframes datapulse-modal-in {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes datapulse-modal-panel-in {
          from {
            opacity: 0;
            transform: translateY(12px) scale(0.985);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .datapulse-chart-modal,
          .datapulse-chart-modal-panel {
            animation: none !important;
          }
          .datapulse-dashboard *,
          .datapulse-dashboard *::before,
          .datapulse-dashboard *::after {
            scroll-behavior: auto !important;
            transition-duration: 0.01ms !important;
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
          }
        }

        @media print {
          .datapulse-chart-modal {
            display: none !important;
          }
        }
      `}</style>

      <div className='datapulse-dashboard min-h-screen bg-stone-50 px-4 py-6 text-slate-900 sm:px-6 lg:px-8'>
        <div className='datapulse-dashboard-inner mx-auto max-w-7xl'>
          <header className='datapulse-print-header relative mb-10 overflow-hidden rounded-3xl border border-stone-200 bg-white px-6 py-7 shadow-sm sm:px-8 sm:py-8'>
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
                  {project.name}
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
                    const previousTitle = document.title;
                    const reportTitle = `${project.name} - DataPulse Report`;

                    document.title = reportTitle;
                    window.setTimeout(() => {
                      window.print();
                      window.setTimeout(() => {
                        document.title = previousTitle;
                      }, 500);
                    }, 0);
                  }}
                  className='datapulse-export-button group inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:bg-slate-800 hover:shadow-md active:translate-y-0'
                >
                  <span className='text-base transition-transform duration-300 group-hover:translate-y-0.5'>
                    ↓
                  </span>

                  <span>Export PDF</span>
                </button>

                <button
                  type='button'
                  onClick={() => window.location.reload()}
                  className='datapulse-refresh-button group inline-flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:border-slate-300 hover:bg-slate-50 hover:shadow-md active:translate-y-0'
                >
                  <span className='text-base transition-transform duration-500 group-hover:rotate-180'>
                    ↻
                  </span>

                  <span>Refresh</span>
                </button>
              </div>
            </div>
          </header>

          {dashboard.kpis?.length > 0 && (
            <section className='datapulse-print-section mb-10'>
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

          <section className='datapulse-print-section'>
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

            {dashboard.charts?.length > 0 ? (
              <div className='datapulse-chart-grid grid gap-6 lg:grid-cols-2'>
                {dashboard.charts.map((chart, index) => (
                  <div
                    key={chart.id || `chart-${index}`}
                    className='datapulse-chart-card'
                  >
                    <ChartCard
                      title={chart.name}
                      chartType={chart.chart_type}
                      onExpand={() => {
                        setExpandedChart(chart);
                      }}
                    >
                      <ChartRenderer
                        chart={chart}
                        data={chartData[chart.id] || []}
                      />
                    </ChartCard>
                  </div>
                ))}
              </div>
            ) : (
              <div className='overflow-hidden rounded-3xl border border-dashed border-stone-300 bg-white p-8 text-center shadow-sm sm:p-12'>
                <div className='mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-xl text-slate-500'>
                  ◌
                </div>
                <h3 className='mt-5 text-lg font-semibold tracking-tight text-slate-900'>
                  No visualizations yet
                </h3>
                <p className='mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500'>
                  DataPulse couldn't generate charts from the current dataset.
                  Your data is still available in the project.
                </p>
                <button
                  type='button'
                  onClick={() => {
                    setLoading(true);
                    setRetryToken((value) => value + 1);
                  }}
                  className='mt-6 rounded-xl border border-stone-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:border-slate-300 hover:bg-slate-50 hover:shadow-md active:translate-y-0'
                >
                  Regenerate analysis
                </button>
              </div>
            )}
          </section>

          {dashboard.insights?.length > 0 && (
            <section className='datapulse-print-section mt-10'>
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
                    className='datapulse-insight-card group rounded-2xl border border-stone-200 bg-white p-5 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md'
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

          <div className='datapulse-print-footer mt-8 border-t border-stone-200 pt-4 text-xs text-slate-400'>
            Generated by DataPulse Analytics · {new Date().toLocaleString()}
          </div>
        </div>
      </div>

      {expandedChart && (
        <div
          className='datapulse-chart-modal fixed inset-0 z-50 flex items-center justify-center bg-slate-950/45 p-3 backdrop-blur-md sm:p-6'
          role='dialog'
          aria-modal='true'
          aria-label={`Expanded ${expandedChart.name} chart`}
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              setExpandedChart(null);
            }
          }}
        >
          <div className='datapulse-chart-modal-panel relative flex max-h-[94vh] w-full max-w-6xl flex-col overflow-hidden rounded-3xl border border-white/60 bg-white shadow-2xl'>
            <div className='flex items-center justify-between gap-4 border-b border-stone-200 bg-white/95 px-5 py-4 backdrop-blur-sm sm:px-7'>
              <div className='min-w-0'>
                <p className='text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400'>
                  DataPulse Analytics
                </p>
                <h2 className='mt-1 truncate text-lg font-semibold tracking-tight text-slate-950 sm:text-xl'>
                  {expandedChart.name}
                </h2>
                <p className='mt-1 text-xs text-slate-500'>
                  {expandedChart.chart_type} visualization
                </p>
              </div>

              <button
                type='button'
                onClick={() => setExpandedChart(null)}
                className='group shrink-0 rounded-xl border border-stone-200 bg-white p-2.5 text-slate-500 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:bg-slate-50 hover:text-slate-900 hover:shadow-md active:translate-y-0'
                aria-label={`Close expanded ${expandedChart.name} chart`}
              >
                <span className='block text-lg leading-none transition-transform duration-200 group-hover:rotate-90'>
                  ×
                </span>
              </button>
            </div>

            <div className='datapulse-expanded-chart min-h-0 flex-1 overflow-auto p-4 sm:p-7'>
              <div className='rounded-2xl border border-stone-200 bg-gradient-to-b from-stone-50/80 to-white p-2 sm:p-4'>
                <ChartRenderer
                  chart={expandedChart}
                  data={chartData[expandedChart.id] || []}
                />
              </div>
            </div>

            <div className='flex items-center justify-between border-t border-stone-200 bg-stone-50/70 px-5 py-3 text-xs text-slate-400 sm:px-7'>
              <span>Press Esc to close</span>
              <span>
                {chartData[expandedChart.id]?.length || 0} data points
              </span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default Dashboard;
