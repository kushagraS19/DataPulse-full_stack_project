// ============================================================
// IMPORTS
// ============================================================

import { useEffect, useState } from 'react';

import { getDatasetInsights } from '../api/insight_api';

// ============================================================
// COMPONENT
// ============================================================

export default function InsightsPanel({ dataset, projectId, workspaceId }) {
  // ==========================================================
  // STATE
  // ==========================================================

  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // ==========================================================
  // LOAD INSIGHTS
  // ==========================================================

  useEffect(() => {
    const loadInsights = async () => {
      if (!dataset?.id) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError('');

        const data = await getDatasetInsights(
          dataset.id,
          projectId,
          workspaceId,
        );

        setInsights(data.insights || []);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load insights.');
      } finally {
        setLoading(false);
      }
    };

    loadInsights();
  }, [dataset?.id, projectId, workspaceId]);

  // ==========================================================
  // LOADING STATE
  // ==========================================================

  if (loading) {
    return (
      <div className='rounded-2xl border border-slate-200 bg-white p-6'>
        <p className='text-sm text-slate-500'>Analyzing your dataset...</p>
      </div>
    );
  }

  // ==========================================================
  // ERROR STATE
  // ==========================================================

  if (error) {
    return (
      <div className='rounded-2xl border border-red-200 bg-red-50 p-6'>
        <p className='text-sm text-red-600'>{error}</p>
      </div>
    );
  }

  // ==========================================================
  // EMPTY STATE
  // ==========================================================

  if (insights.length === 0) {
    return (
      <div className='rounded-2xl border border-slate-200 bg-white p-6'>
        <h2 className='text-lg font-semibold text-slate-900'>Insights</h2>

        <p className='mt-2 text-sm text-slate-500'>
          No significant patterns were detected in this dataset.
        </p>
      </div>
    );
  }

  // ==========================================================
  // HELPERS
  // ==========================================================

  const getSeverityClasses = (severity) => {
    if (severity === 'critical') {
      return 'border-red-300 bg-red-50';
    }

    if (severity === 'warning') {
      return 'border-amber-300 bg-amber-50';
    }

    if (severity === 'success') {
      return 'border-emerald-300 bg-emerald-50';
    }

    return 'border-slate-200 bg-white';
  };

  const getSeverityLabel = (severity) => {
    if (severity === 'critical') {
      return 'Critical';
    }

    if (severity === 'warning') {
      return 'Warning';
    }

    if (severity === 'success') {
      return 'Positive';
    }

    return 'Info';
  };

  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <section className='space-y-4'>
      <div>
        <h2 className='text-xl font-semibold text-slate-900'>
          Automatic Insights
        </h2>

        <p className='mt-1 text-sm text-slate-500'>
          Patterns and data-quality signals detected automatically from your
          dataset.
        </p>
      </div>

      <div className='grid gap-4'>
        {insights.map((insight, index) => (
          <article
            key={`${insight.type}-${insight.column || index}-${index}`}
            className={`rounded-2xl border p-5 ${getSeverityClasses(
              insight.severity,
            )}`}
          >
            <div className='flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between'>
              <div>
                <h3 className='font-semibold text-slate-900'>
                  {insight.title}
                </h3>

                <p className='mt-2 text-sm leading-6 text-slate-600'>
                  {insight.description}
                </p>
              </div>

              <span className='w-fit rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-600'>
                {getSeverityLabel(insight.severity)}
              </span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
