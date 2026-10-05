import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { createWorkspace, getWorkspaces } from '../api/workspace_api';
import { createProject, getWorkspaceProjects } from '../api/project_api';

function Workspace() {
  const navigate = useNavigate();

  const [workspaces, setWorkspaces] = useState([]);
  const [selectedWorkspace, setSelectedWorkspace] = useState(null);
  const [projects, setProjects] = useState([]);

  const [workspaceName, setWorkspaceName] = useState('');
  const [projectName, setProjectName] = useState('');

  const [loading, setLoading] = useState(true);
  const [projectsLoading, setProjectsLoading] = useState(false);

  const [error, setError] = useState('');
  const [projectError, setProjectError] = useState('');

  const [creatingWorkspace, setCreatingWorkspace] = useState(false);
  const [creatingProject, setCreatingProject] = useState(false);

  const loadWorkspaces = async () => {
    try {
      setLoading(true);
      setError('');

      const data = await getWorkspaces();

      setWorkspaces(data);

      if (data.length > 0) {
        setSelectedWorkspace(data[0]);
      } else {
        setSelectedWorkspace(null);
      }
    } catch (error) {
      console.error('Failed to load workspaces:', error);

      setError(error.response?.data?.detail || 'Failed to load workspaces');
    } finally {
      setLoading(false);
    }
  };

  const loadProjects = async (workspaceId) => {
    try {
      setProjectsLoading(true);
      setProjectError('');

      const data = await getWorkspaceProjects(workspaceId);

      setProjects(data);
    } catch (error) {
      console.error('Failed to load projects:', error);

      setProjectError(
        error.response?.data?.detail || 'Failed to load projects',
      );

      setProjects([]);
    } finally {
      setProjectsLoading(false);
    }
  };

  useEffect(() => {
    loadWorkspaces();
  }, []);

  useEffect(() => {
    if (!selectedWorkspace) {
      setProjects([]);
      return;
    }

    loadProjects(selectedWorkspace.id);
  }, [selectedWorkspace]);

  const handleCreateWorkspace = async (event) => {
    event.preventDefault();

    if (!workspaceName.trim() || creatingWorkspace) {
      return;
    }

    try {
      setCreatingWorkspace(true);
      setError('');

      const workspace = await createWorkspace({
        name: workspaceName.trim(),
      });

      setWorkspaces((previousWorkspaces) => [...previousWorkspaces, workspace]);

      setSelectedWorkspace(workspace);
      setWorkspaceName('');
    } catch (error) {
      console.error('Failed to create workspace:', error);

      setError(error.response?.data?.detail || 'Failed to create workspace');
    } finally {
      setCreatingWorkspace(false);
    }
  };

  const handleCreateProject = async (event) => {
    event.preventDefault();

    if (!selectedWorkspace || !projectName.trim() || creatingProject) {
      return;
    }

    try {
      setCreatingProject(true);
      setProjectError('');

      const project = await createProject({
        name: projectName.trim(),
        workspace_id: selectedWorkspace.id,
      });

      setProjects((previousProjects) => [...previousProjects, project]);

      setProjectName('');
    } catch (error) {
      console.error('Failed to create project:', error);

      setProjectError(
        error.response?.data?.detail || 'Failed to create project',
      );
    } finally {
      setCreatingProject(false);
    }
  };

  const handleProjectSelect = (project) => {
    navigate(`/workspaces/${selectedWorkspace.id}/projects/${project.id}`);
  };

  if (loading) {
    return (
      <div className='min-h-screen bg-stone-50 px-4 py-6 sm:px-6 lg:px-8'>
        <div className='mx-auto w-full max-w-7xl'>
          <div className='animate-pulse'>
            <div className='h-3 w-24 rounded-full bg-stone-200' />
            <div className='mt-3 h-10 w-72 rounded-xl bg-stone-200' />
            <div className='mt-3 h-5 w-96 max-w-full rounded-lg bg-stone-200' />

            <div className='mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3'>
              {[1, 2, 3].map((item) => (
                <div
                  key={item}
                  className='h-36 rounded-3xl border border-stone-200 bg-white'
                />
              ))}
            </div>

            <div className='mt-8 h-80 rounded-3xl border border-stone-200 bg-white' />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className='min-h-screen overflow-hidden bg-stone-50'>
      {/* Ambient background */}
      <div className='pointer-events-none fixed inset-0 overflow-hidden'>
        <div className='absolute -left-40 top-20 h-80 w-80 rounded-full bg-slate-200/30 blur-3xl animate-[workspaceFloat_14s_ease-in-out_infinite]' />

        <div className='absolute -right-40 top-1/3 h-96 w-96 rounded-full bg-stone-200/40 blur-3xl animate-[workspaceFloatReverse_17s_ease-in-out_infinite]' />
      </div>

      <div className='relative z-10 mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8 lg:py-10'>
        {/* Header */}
        <header className='animate-[workspaceFadeUp_550ms_cubic-bezier(.22,1,.36,1)_both]'>
          <div className='flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between'>
            <div className='min-w-0'>
              <div className='flex items-center gap-2'>
                <span className='h-1.5 w-1.5 rounded-full bg-slate-900' />

                <p className='text-[11px] font-bold uppercase tracking-[0.2em] text-slate-400'>
                  DataPulse
                </p>
              </div>

              <h1 className='mt-3 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl'>
                Your workspaces
              </h1>

              <p className='mt-2 max-w-2xl text-sm leading-6 text-slate-500 sm:text-base'>
                Organize your analytics projects, datasets, and dashboards in
                one place.
              </p>
            </div>

            {/* Create workspace */}
            <form
              onSubmit={handleCreateWorkspace}
              className='flex w-full max-w-xl flex-col gap-2 sm:flex-row lg:w-auto'
            >
              <div className='group relative flex-1 sm:min-w-[270px]'>
                <input
                  type='text'
                  placeholder='New workspace name'
                  value={workspaceName}
                  onChange={(event) => setWorkspaceName(event.target.value)}
                  disabled={creatingWorkspace}
                  className='h-12 w-full rounded-xl border border-stone-200 bg-white px-4 text-sm text-slate-900 shadow-sm outline-none transition-all duration-300 placeholder:text-slate-400 hover:border-stone-300 hover:shadow-md focus:border-slate-400 focus:ring-4 focus:ring-slate-900/5 disabled:cursor-not-allowed disabled:bg-stone-100'
                />
              </div>

              <button
                type='submit'
                disabled={!workspaceName.trim() || creatingWorkspace}
                className='group relative h-12 overflow-hidden rounded-xl bg-slate-950 px-5 text-sm font-semibold text-white shadow-lg shadow-slate-900/10 transition-all duration-300 hover:-translate-y-0.5 hover:bg-slate-800 hover:shadow-xl active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0'
              >
                <span className='absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/10 to-transparent transition-transform duration-700 group-hover:translate-x-full' />

                <span className='relative flex items-center justify-center gap-2'>
                  {creatingWorkspace && (
                    <span className='h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white' />
                  )}

                  {creatingWorkspace ? 'Creating...' : 'Create workspace'}

                  {!creatingWorkspace && (
                    <span className='text-base transition-transform duration-200 group-hover:translate-x-0.5'>
                      +
                    </span>
                  )}
                </span>
              </button>
            </form>
          </div>
        </header>

        {/* Workspace error */}
        {error && (
          <div className='mt-6 flex animate-[workspaceErrorIn_400ms_ease-out_both] items-start gap-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3.5 text-sm text-red-700 shadow-sm'>
            <span className='flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-red-100 text-xs font-bold'>
              !
            </span>

            <div className='min-w-0'>
              <p className='font-semibold'>Something went wrong</p>

              <p className='mt-0.5 break-words text-red-600'>{error}</p>
            </div>
          </div>
        )}

        {/* Workspace section */}
        <section className='mt-10'>
          <div className='mb-5 flex items-end justify-between gap-4'>
            <div>
              <div className='flex items-center gap-3'>
                <h2 className='text-lg font-bold text-slate-950'>Workspaces</h2>

                {workspaces.length > 0 && (
                  <span className='rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-500'>
                    {workspaces.length}
                  </span>
                )}
              </div>

              <p className='mt-1 text-sm text-slate-500'>
                Select a workspace to view its projects.
              </p>
            </div>

            {selectedWorkspace && (
              <div className='hidden items-center gap-2 text-xs font-medium text-slate-400 sm:flex'>
                <span className='h-1.5 w-1.5 rounded-full bg-emerald-500' />
                Workspace active
              </div>
            )}
          </div>

          {workspaces.length === 0 ? (
            <div className='relative overflow-hidden rounded-3xl border border-dashed border-stone-300 bg-white px-6 py-16 text-center shadow-sm'>
              <div className='pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-stone-300 to-transparent' />

              <div className='mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-950 text-xl font-light text-white shadow-lg shadow-slate-900/10'>
                +
              </div>

              <h3 className='mt-5 text-lg font-bold text-slate-950'>
                No workspaces yet
              </h3>

              <p className='mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500'>
                Create your first workspace above to start organizing your
                analytics projects.
              </p>
            </div>
          ) : (
            <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-3'>
              {workspaces.map((workspace, index) => {
                const isSelected = selectedWorkspace?.id === workspace.id;

                return (
                  <button
                    key={workspace.id}
                    type='button'
                    onClick={() => setSelectedWorkspace(workspace)}
                    style={{
                      animationDelay: `${index * 70}ms`,
                    }}
                    className={`group relative overflow-hidden rounded-3xl border p-5 text-left animate-[workspaceCardIn_500ms_cubic-bezier(.22,1,.36,1)_both] transition-all duration-300 ${
                      isSelected
                        ? 'border-slate-900 bg-slate-950 text-white shadow-xl shadow-slate-900/15'
                        : 'border-stone-200 bg-white text-slate-900 shadow-sm hover:-translate-y-1 hover:border-stone-300 hover:shadow-xl'
                    }`}
                  >
                    {/* Active glow */}
                    {isSelected && (
                      <div className='pointer-events-none absolute -right-12 -top-12 h-32 w-32 rounded-full bg-white/[0.05] blur-2xl' />
                    )}

                    <div className='relative flex items-start justify-between gap-4'>
                      <div
                        className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-sm font-bold transition-all duration-300 ${
                          isSelected
                            ? 'bg-white text-slate-950 shadow-lg'
                            : 'bg-stone-100 text-slate-700 group-hover:bg-slate-950 group-hover:text-white group-hover:shadow-md'
                        }`}
                      >
                        {workspace.name?.charAt(0)?.toUpperCase() || 'W'}
                      </div>

                      {isSelected ? (
                        <span className='rounded-full border border-white/10 bg-white/[0.08] px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-300'>
                          Active
                        </span>
                      ) : (
                        <span className='text-lg text-slate-300 transition-all duration-300 group-hover:translate-x-1 group-hover:text-slate-700'>
                          →
                        </span>
                      )}
                    </div>

                    <div className='relative mt-6'>
                      <h3
                        className={`truncate text-base font-bold ${
                          isSelected ? 'text-white' : 'text-slate-950'
                        }`}
                      >
                        {workspace.name}
                      </h3>

                      <p
                        className={`mt-1 text-xs ${
                          isSelected ? 'text-slate-400' : 'text-slate-400'
                        }`}
                      >
                        Analytics workspace
                      </p>
                    </div>

                    <div
                      className={`mt-5 h-px transition-colors duration-300 ${
                        isSelected
                          ? 'bg-white/10'
                          : 'bg-stone-100 group-hover:bg-stone-200'
                      }`}
                    />

                    <div
                      className={`mt-4 flex items-center gap-1.5 text-xs font-semibold transition-colors duration-200 ${
                        isSelected
                          ? 'text-slate-300'
                          : 'text-slate-400 group-hover:text-slate-800'
                      }`}
                    >
                      {isSelected ? 'Currently selected' : 'Select workspace'}

                      {!isSelected && (
                        <span className='transition-transform duration-200 group-hover:translate-x-1'>
                          →
                        </span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </section>

        {/* Selected workspace */}
        {selectedWorkspace && (
          <section className='mt-10 overflow-hidden rounded-[2rem] border border-stone-200 bg-white shadow-sm animate-[workspacePanelIn_550ms_cubic-bezier(.22,1,.36,1)_both]'>
            {/* Workspace header */}
            <div className='relative overflow-hidden border-b border-stone-100 px-5 py-6 sm:px-7'>
              <div className='pointer-events-none absolute -right-20 -top-28 h-56 w-56 rounded-full bg-stone-100/70 blur-3xl' />

              <div className='relative flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between'>
                <div className='min-w-0'>
                  <div className='flex items-center gap-2'>
                    <span className='h-1.5 w-1.5 rounded-full bg-emerald-500' />

                    <p className='text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400'>
                      Selected workspace
                    </p>
                  </div>

                  <h2 className='mt-2 truncate text-2xl font-bold tracking-tight text-slate-950'>
                    {selectedWorkspace.name}
                  </h2>

                  <p className='mt-1 text-sm text-slate-500'>
                    Manage and open projects inside this workspace.
                  </p>
                </div>

                {/* Create project */}
                <form
                  onSubmit={handleCreateProject}
                  className='flex w-full max-w-xl flex-col gap-2 sm:flex-row lg:w-auto'
                >
                  <input
                    type='text'
                    placeholder='New project name'
                    value={projectName}
                    onChange={(event) => setProjectName(event.target.value)}
                    disabled={creatingProject}
                    className='h-11 min-w-0 flex-1 rounded-xl border border-stone-200 bg-stone-50 px-3.5 text-sm text-slate-900 outline-none transition-all duration-300 placeholder:text-slate-400 hover:border-stone-300 hover:bg-white focus:border-slate-400 focus:bg-white focus:ring-4 focus:ring-slate-900/5 disabled:cursor-not-allowed disabled:opacity-60 sm:min-w-[240px]'
                  />

                  <button
                    type='submit'
                    disabled={!projectName.trim() || creatingProject}
                    className='group h-11 rounded-xl bg-slate-900 px-4 text-sm font-semibold text-white shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:bg-slate-800 hover:shadow-md active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0'
                  >
                    <span className='flex items-center justify-center gap-2'>
                      {creatingProject && (
                        <span className='h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white' />
                      )}

                      {creatingProject ? 'Creating...' : 'New project'}

                      {!creatingProject && (
                        <span className='transition-transform duration-200 group-hover:rotate-90'>
                          +
                        </span>
                      )}
                    </span>
                  </button>
                </form>
              </div>
            </div>

            {/* Project error */}
            {projectError && (
              <div className='mx-5 mt-5 flex animate-[workspaceErrorIn_400ms_ease-out_both] items-start gap-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3.5 text-sm text-red-700 sm:mx-7'>
                <span className='flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-red-100 text-xs font-bold'>
                  !
                </span>

                <div className='min-w-0'>
                  <p className='font-semibold'>Could not load projects</p>

                  <p className='mt-0.5 break-words text-red-600'>
                    {projectError}
                  </p>
                </div>
              </div>
            )}

            {/* Projects */}
            <div className='px-5 py-7 sm:px-7'>
              <div className='mb-5 flex items-end justify-between gap-4'>
                <div>
                  <h3 className='text-base font-bold text-slate-950'>
                    Projects
                  </h3>

                  <p className='mt-1 text-sm text-slate-500'>
                    Open a project to access its analytics dashboard.
                  </p>
                </div>

                {!projectsLoading && projects.length > 0 && (
                  <span className='shrink-0 rounded-full bg-stone-100 px-2.5 py-1 text-xs font-semibold text-slate-500'>
                    {projects.length}{' '}
                    {projects.length === 1 ? 'project' : 'projects'}
                  </span>
                )}
              </div>

              {projectsLoading ? (
                <div className='grid gap-3 sm:grid-cols-2 lg:grid-cols-3'>
                  {[1, 2, 3].map((item) => (
                    <div
                      key={item}
                      className='animate-pulse rounded-2xl border border-stone-200 bg-stone-50 p-5'
                    >
                      <div className='h-10 w-10 rounded-xl bg-stone-200' />
                      <div className='mt-5 h-4 w-32 rounded bg-stone-200' />
                      <div className='mt-2 h-3 w-24 rounded bg-stone-200' />
                      <div className='mt-5 h-3 w-20 rounded bg-stone-200' />
                    </div>
                  ))}
                </div>
              ) : projects.length === 0 ? (
                <div className='relative overflow-hidden rounded-2xl border border-dashed border-stone-300 bg-stone-50 px-6 py-14 text-center'>
                  <div className='mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-xl text-slate-500 shadow-sm ring-1 ring-stone-200'>
                    +
                  </div>

                  <h4 className='mt-4 text-sm font-bold text-slate-900'>
                    No projects yet
                  </h4>

                  <p className='mx-auto mt-1.5 max-w-sm text-sm leading-6 text-slate-500'>
                    Create a project above and start building your analytics
                    workspace.
                  </p>
                </div>
              ) : (
                <div className='grid gap-3 sm:grid-cols-2 lg:grid-cols-3'>
                  {projects.map((project, index) => (
                    <button
                      key={project.id}
                      type='button'
                      onClick={() => handleProjectSelect(project)}
                      style={{
                        animationDelay: `${index * 60}ms`,
                      }}
                      className='group relative overflow-hidden rounded-2xl border border-stone-200 bg-white p-5 text-left shadow-sm animate-[workspaceProjectIn_450ms_cubic-bezier(.22,1,.36,1)_both] transition-all duration-300 hover:-translate-y-1 hover:border-slate-300 hover:shadow-xl'
                    >
                      <div className='absolute inset-x-0 top-0 h-px origin-left scale-x-0 bg-slate-900 transition-transform duration-300 group-hover:scale-x-100' />

                      <div className='flex items-start justify-between gap-4'>
                        <div className='flex h-10 w-10 items-center justify-center rounded-xl bg-stone-100 text-sm font-bold text-slate-700 transition-all duration-300 group-hover:bg-slate-950 group-hover:text-white group-hover:shadow-md'>
                          {project.name?.charAt(0)?.toUpperCase() || 'P'}
                        </div>

                        <span className='text-lg text-slate-300 transition-all duration-300 group-hover:translate-x-1 group-hover:text-slate-700'>
                          →
                        </span>
                      </div>

                      <h4 className='mt-5 truncate text-base font-bold text-slate-950'>
                        {project.name}
                      </h4>

                      <p className='mt-1 text-xs text-slate-400'>
                        Analytics project
                      </p>

                      <div className='mt-4 flex items-center gap-1.5 text-xs font-semibold text-slate-400 transition-colors duration-200 group-hover:text-slate-900'>
                        Open project
                        <span className='transition-transform duration-200 group-hover:translate-x-1'>
                          →
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </section>
        )}
      </div>

      <style>{`
        @keyframes workspaceFadeUp {
          from {
            opacity: 0;
            transform: translateY(14px);
          }

          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes workspaceCardIn {
          from {
            opacity: 0;
            transform: translateY(14px) scale(0.985);
          }

          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }

        @keyframes workspacePanelIn {
          from {
            opacity: 0;
            transform: translateY(16px);
          }

          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes workspaceProjectIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }

          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes workspaceErrorIn {
          0% {
            opacity: 0;
            transform: translateY(-6px);
          }

          100% {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes workspaceFloat {
          0%,
          100% {
            transform: translate3d(0, 0, 0);
          }

          50% {
            transform: translate3d(35px, 25px, 0);
          }
        }

        @keyframes workspaceFloatReverse {
          0%,
          100% {
            transform: translate3d(0, 0, 0);
          }

          50% {
            transform: translate3d(-30px, -25px, 0);
          }
        }

        @media (prefers-reduced-motion: reduce) {
          *,
          *::before,
          *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            scroll-behavior: auto !important;
            transition-duration: 0.01ms !important;
          }
        }
      `}</style>
    </div>
  );
}

export default Workspace;
