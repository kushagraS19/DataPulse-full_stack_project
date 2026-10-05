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
        <div className='mx-auto w-full max-w-7xl animate-pulse'>
          <div className='h-8 w-48 rounded-lg bg-stone-200' />

          <div className='mt-3 h-4 w-72 rounded bg-stone-200' />

          <div className='mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3'>
            <div className='h-28 rounded-2xl bg-white ring-1 ring-stone-200' />
            <div className='h-28 rounded-2xl bg-white ring-1 ring-stone-200' />
            <div className='h-28 rounded-2xl bg-white ring-1 ring-stone-200' />
          </div>

          <div className='mt-8 h-72 rounded-2xl bg-white ring-1 ring-stone-200' />
        </div>
      </div>
    );
  }

  return (
    <div className='min-h-screen bg-stone-50'>
      <div className='mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8 lg:py-10'>
        {/* Header */}
        <div className='flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between'>
          <div>
            <p className='text-xs font-bold uppercase tracking-[0.18em] text-slate-400'>
              DataPulse
            </p>

            <h1 className='mt-2 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl'>
              Your workspaces
            </h1>

            <p className='mt-2 max-w-2xl text-sm leading-6 text-slate-500 sm:text-base'>
              Organize your analytics projects, datasets, and dashboards in one
              place.
            </p>
          </div>

          <form
            onSubmit={handleCreateWorkspace}
            className='flex w-full flex-col gap-2 sm:w-auto sm:min-w-[320px] sm:flex-row'
          >
            <input
              type='text'
              placeholder='New workspace name'
              value={workspaceName}
              onChange={(event) => setWorkspaceName(event.target.value)}
              disabled={creatingWorkspace}
              className='h-11 min-w-0 flex-1 rounded-xl border border-stone-200 bg-white px-3.5 text-sm text-slate-900 outline-none transition-all duration-200 placeholder:text-slate-400 focus:border-slate-400 focus:ring-4 focus:ring-slate-900/5 disabled:cursor-not-allowed disabled:bg-stone-100'
            />

            <button
              type='submit'
              disabled={!workspaceName.trim() || creatingWorkspace}
              className='h-11 rounded-xl bg-slate-900 px-4 text-sm font-semibold text-white shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:bg-slate-800 hover:shadow-md active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0'
            >
              {creatingWorkspace ? 'Creating...' : 'Create'}
            </button>
          </form>
        </div>

        {/* Workspace error */}
        {error && (
          <div className='mt-6 flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3.5 text-sm text-red-700 shadow-sm'>
            <span className='mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-red-100 text-xs font-bold'>
              !
            </span>

            <div>
              <p className='font-semibold'>Something went wrong</p>
              <p className='mt-0.5 text-red-600'>{error}</p>
            </div>
          </div>
        )}

        {/* Workspace list */}
        <section className='mt-8'>
          <div className='mb-4 flex items-center justify-between'>
            <div>
              <h2 className='text-lg font-bold text-slate-950'>Workspaces</h2>

              <p className='mt-1 text-sm text-slate-500'>
                Select a workspace to view its projects.
              </p>
            </div>

            {workspaces.length > 0 && (
              <span className='rounded-full border border-stone-200 bg-white px-3 py-1 text-xs font-semibold text-slate-500'>
                {workspaces.length}{' '}
                {workspaces.length === 1 ? 'workspace' : 'workspaces'}
              </span>
            )}
          </div>

          {workspaces.length === 0 ? (
            <div className='rounded-2xl border border-dashed border-stone-300 bg-white px-6 py-14 text-center shadow-sm'>
              <div className='mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-stone-100 text-xl text-slate-500'>
                □
              </div>

              <h3 className='mt-4 text-base font-bold text-slate-900'>
                No workspaces yet
              </h3>

              <p className='mx-auto mt-2 max-w-sm text-sm leading-6 text-slate-500'>
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
                    className={`group animate-[fadeInUp_450ms_ease-out_both] rounded-2xl border p-5 text-left transition-all duration-300 ${
                      isSelected
                        ? 'border-slate-900 bg-slate-900 text-white shadow-lg shadow-slate-900/10'
                        : 'border-stone-200 bg-white text-slate-900 shadow-sm hover:-translate-y-1 hover:border-stone-300 hover:shadow-md'
                    }`}
                  >
                    <div className='flex items-start justify-between gap-4'>
                      <div
                        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-sm font-bold transition-colors duration-300 ${
                          isSelected
                            ? 'bg-white/10 text-white'
                            : 'bg-stone-100 text-slate-700 group-hover:bg-slate-900 group-hover:text-white'
                        }`}
                      >
                        {workspace.name?.charAt(0)?.toUpperCase() || 'W'}
                      </div>

                      {isSelected && (
                        <span className='rounded-full bg-white/10 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-white'>
                          Active
                        </span>
                      )}
                    </div>

                    <h3
                      className={`mt-5 truncate text-base font-bold ${
                        isSelected ? 'text-white' : 'text-slate-950'
                      }`}
                    >
                      {workspace.name}
                    </h3>

                    <p
                      className={`mt-1 text-xs ${
                        isSelected ? 'text-slate-300' : 'text-slate-400'
                      }`}
                    >
                      Workspace
                    </p>
                  </button>
                );
              })}
            </div>
          )}
        </section>

        {/* Selected workspace */}
        {selectedWorkspace && (
          <section className='mt-10 overflow-hidden rounded-3xl border border-stone-200 bg-white shadow-sm'>
            <div className='border-b border-stone-100 px-5 py-5 sm:px-7'>
              <div className='flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between'>
                <div className='min-w-0'>
                  <p className='text-xs font-bold uppercase tracking-[0.16em] text-slate-400'>
                    Selected workspace
                  </p>

                  <h2 className='mt-1 truncate text-2xl font-bold tracking-tight text-slate-950'>
                    {selectedWorkspace.name}
                  </h2>

                  <p className='mt-1 text-sm text-slate-500'>
                    Manage and open projects inside this workspace.
                  </p>
                </div>

                <form
                  onSubmit={handleCreateProject}
                  className='flex w-full flex-col gap-2 sm:w-auto sm:min-w-[320px] sm:flex-row'
                >
                  <input
                    type='text'
                    placeholder='New project name'
                    value={projectName}
                    onChange={(event) => setProjectName(event.target.value)}
                    disabled={creatingProject}
                    className='h-11 min-w-0 flex-1 rounded-xl border border-stone-200 bg-stone-50 px-3.5 text-sm text-slate-900 outline-none transition-all duration-200 placeholder:text-slate-400 focus:border-slate-400 focus:bg-white focus:ring-4 focus:ring-slate-900/5 disabled:cursor-not-allowed disabled:opacity-60'
                  />

                  <button
                    type='submit'
                    disabled={!projectName.trim() || creatingProject}
                    className='h-11 rounded-xl bg-slate-900 px-4 text-sm font-semibold text-white shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:bg-slate-800 hover:shadow-md active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0'
                  >
                    {creatingProject ? 'Creating...' : 'New Project'}
                  </button>
                </form>
              </div>
            </div>

            {/* Project error */}
            {projectError && (
              <div className='mx-5 mt-5 flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3.5 text-sm text-red-700 sm:mx-7'>
                <span className='mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-red-100 text-xs font-bold'>
                  !
                </span>

                <div>
                  <p className='font-semibold'>Could not load projects</p>

                  <p className='mt-0.5 text-red-600'>{projectError}</p>
                </div>
              </div>
            )}

            {/* Projects */}
            <div className='px-5 py-6 sm:px-7'>
              <div className='mb-4 flex items-center justify-between'>
                <div>
                  <h3 className='text-base font-bold text-slate-950'>
                    Projects
                  </h3>

                  <p className='mt-1 text-sm text-slate-500'>
                    Open a project to access its analytics dashboard.
                  </p>
                </div>

                {!projectsLoading && projects.length > 0 && (
                  <span className='text-xs font-semibold text-slate-400'>
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
                    </div>
                  ))}
                </div>
              ) : projects.length === 0 ? (
                <div className='rounded-2xl border border-dashed border-stone-300 bg-stone-50 px-6 py-12 text-center'>
                  <div className='mx-auto flex h-11 w-11 items-center justify-center rounded-xl bg-white text-lg text-slate-400 ring-1 ring-stone-200'>
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
                      className='group animate-[fadeInUp_400ms_ease-out_both] rounded-2xl border border-stone-200 bg-white p-5 text-left shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-slate-300 hover:shadow-lg'
                    >
                      <div className='flex items-start justify-between gap-4'>
                        <div className='flex h-10 w-10 items-center justify-center rounded-xl bg-stone-100 text-sm font-bold text-slate-700 transition-all duration-300 group-hover:bg-slate-900 group-hover:text-white group-hover:shadow-md'>
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

                      <div className='mt-4 flex items-center gap-1.5 text-xs font-semibold text-slate-500 transition-colors duration-200 group-hover:text-slate-900'>
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
        @keyframes fadeInUp {
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
          * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
          }
        }
      `}</style>
    </div>
  );
}

export default Workspace;
