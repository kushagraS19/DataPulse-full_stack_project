import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { getWorkspaces } from '../api/workspace_api';

function Home() {
  const navigate = useNavigate();

  const [workspaces, setWorkspaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadHomeData = async () => {
      try {
        setLoading(true);
        setError('');

        const data = await getWorkspaces();

        setWorkspaces(data);
      } catch (error) {
        console.error('Failed to load home data:', error);

        setError(
          error.response?.data?.detail || 'Failed to load your workspaces',
        );
      } finally {
        setLoading(false);
      }
    };

    loadHomeData();
  }, []);

  return (
    <div className='min-h-screen bg-stone-50'>
      <div className='mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8 lg:py-10'>
        {/* Hero */}
        <section className='relative overflow-hidden rounded-[2rem] bg-slate-950 px-6 py-10 text-white shadow-xl shadow-slate-900/10 sm:px-10 sm:py-12 lg:px-12'>
          <div className='pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full bg-white/[0.04] blur-2xl' />

          <div className='pointer-events-none absolute -bottom-32 left-1/3 h-72 w-72 rounded-full bg-slate-400/[0.06] blur-3xl' />

          <div className='relative z-10 max-w-3xl'>
            <p className='animate-[homeFadeIn_500ms_ease-out_both] text-xs font-bold uppercase tracking-[0.2em] text-slate-400'>
              DataPulse Analytics
            </p>

            <h1 className='mt-4 animate-[homeFadeIn_600ms_100ms_ease-out_both] text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl'>
              Turn your data into
              <span className='block text-slate-400'>something useful.</span>
            </h1>

            <p className='mt-5 max-w-2xl animate-[homeFadeIn_600ms_200ms_ease-out_both] text-sm leading-7 text-slate-400 sm:text-base'>
              Upload datasets, discover patterns, build analytics dashboards,
              and understand what your data is actually telling you.
            </p>

            <div className='mt-8 flex flex-col gap-3 sm:flex-row'>
              <button
                type='button'
                onClick={() => navigate('/workspace')}
                className='group inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-white px-5 text-sm font-semibold text-slate-950 shadow-lg transition-all duration-300 hover:-translate-y-0.5 hover:bg-stone-100 hover:shadow-xl active:translate-y-0'
              >
                Manage workspaces
                <span className='transition-transform duration-200 group-hover:translate-x-1'>
                  →
                </span>
              </button>

              {workspaces.length > 0 && (
                <button
                  type='button'
                  onClick={() =>
                    navigate(`/workspaces/${workspaces[0].id}/projects`)
                  }
                  className='inline-flex h-11 items-center justify-center rounded-xl border border-white/10 bg-white/[0.05] px-5 text-sm font-semibold text-white transition-all duration-300 hover:bg-white/[0.1]'
                >
                  View workspace
                </button>
              )}
            </div>
          </div>
        </section>

        {/* Error */}
        {error && (
          <div className='mt-6 rounded-2xl border border-red-200 bg-red-50 px-4 py-3.5 text-sm text-red-700'>
            {error}
          </div>
        )}

        {/* Workspace overview */}
        <section className='mt-10'>
          <div className='flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between'>
            <div>
              <p className='text-xs font-bold uppercase tracking-[0.16em] text-slate-400'>
                Overview
              </p>

              <h2 className='mt-1 text-2xl font-bold tracking-tight text-slate-950'>
                Your workspaces
              </h2>

              <p className='mt-1 text-sm text-slate-500'>
                Jump back into your analytics projects.
              </p>
            </div>

            <button
              type='button'
              onClick={() => navigate('/workspace')}
              className='text-sm font-semibold text-slate-600 transition-colors hover:text-slate-950'
            >
              Manage all →
            </button>
          </div>

          {loading ? (
            <div className='mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3'>
              {[1, 2, 3].map((item) => (
                <div
                  key={item}
                  className='h-36 animate-pulse rounded-2xl border border-stone-200 bg-white'
                />
              ))}
            </div>
          ) : workspaces.length === 0 ? (
            <div className='mt-5 rounded-2xl border border-dashed border-stone-300 bg-white px-6 py-12 text-center'>
              <div className='mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-stone-100 text-xl text-slate-500'>
                +
              </div>

              <h3 className='mt-4 text-base font-bold text-slate-900'>
                Start your first workspace
              </h3>

              <p className='mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500'>
                Create a workspace to organize your projects and datasets.
              </p>

              <button
                type='button'
                onClick={() => navigate('/workspace')}
                className='mt-5 rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition-all duration-200 hover:-translate-y-0.5 hover:bg-slate-800 hover:shadow-md'
              >
                Create workspace
              </button>
            </div>
          ) : (
            <div className='mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3'>
              {workspaces.slice(0, 6).map((workspace, index) => (
                <button
                  key={workspace.id}
                  type='button'
                  onClick={() => navigate('/workspace')}
                  style={{
                    animationDelay: `${index * 70}ms`,
                  }}
                  className='group animate-[homeCardIn_450ms_ease-out_both] rounded-2xl border border-stone-200 bg-white p-5 text-left shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-stone-300 hover:shadow-lg'
                >
                  <div className='flex items-start justify-between gap-4'>
                    <div className='flex h-11 w-11 items-center justify-center rounded-xl bg-stone-100 text-sm font-bold text-slate-700 transition-all duration-300 group-hover:bg-slate-900 group-hover:text-white'>
                      {workspace.name?.charAt(0)?.toUpperCase() || 'W'}
                    </div>

                    <span className='text-lg text-slate-300 transition-all duration-200 group-hover:translate-x-1 group-hover:text-slate-700'>
                      →
                    </span>
                  </div>

                  <h3 className='mt-5 truncate text-base font-bold text-slate-950'>
                    {workspace.name}
                  </h3>

                  <p className='mt-1 text-xs text-slate-400'>
                    Analytics workspace
                  </p>
                </button>
              ))}
            </div>
          )}
        </section>

        {/* Quick actions */}
        <section className='mt-10'>
          <p className='text-xs font-bold uppercase tracking-[0.16em] text-slate-400'>
            Quick actions
          </p>

          <div className='mt-4 grid gap-4 sm:grid-cols-2'>
            <button
              type='button'
              onClick={() => navigate('/workspace')}
              className='group rounded-2xl border border-stone-200 bg-white p-5 text-left shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-stone-300 hover:shadow-md'
            >
              <div className='flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-slate-700 transition-all duration-300 group-hover:bg-slate-900 group-hover:text-white'>
                +
              </div>

              <h3 className='mt-4 text-base font-bold text-slate-950'>
                Create workspace
              </h3>

              <p className='mt-1 text-sm leading-6 text-slate-500'>
                Start a new space for a project, team, or dataset.
              </p>
            </button>

            <button
              type='button'
              onClick={() => navigate('/workspace')}
              className='group rounded-2xl border border-stone-200 bg-white p-5 text-left shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-stone-300 hover:shadow-md'
            >
              <div className='flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-slate-700 transition-all duration-300 group-hover:bg-slate-900 group-hover:text-white'>
                ▦
              </div>

              <h3 className='mt-4 text-base font-bold text-slate-950'>
                Browse projects
              </h3>

              <p className='mt-1 text-sm leading-6 text-slate-500'>
                Open your existing workspaces and continue analyzing data.
              </p>
            </button>
          </div>
        </section>
      </div>

      <style>{`
        @keyframes homeFadeIn {
          from {
            opacity: 0;
            transform: translateY(12px);
          }

          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes homeCardIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }

          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @media (prefers-reduced-motion: reduce) {
          *,
          *::before,
          *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
          }
        }
      `}</style>
    </div>
  );
}

export default Home;
