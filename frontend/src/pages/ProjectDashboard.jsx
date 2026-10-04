import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { getProject } from '../api/project_api';
import Dashboard from './Dashboard';

function ProjectDashboard() {
  const { workspaceId, projectId } = useParams();

  const navigate = useNavigate();

  const [project, setProject] = useState(null);
  const [workspace, setWorkspace] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadProject = async () => {
      try {
        setLoading(true);
        setError('');

        if (!workspaceId || !projectId) {
          throw new Error('Workspace or project ID is missing');
        }

        const projectResponse = await getProject(
          Number(projectId),
          Number(workspaceId),
        );

        setProject(projectResponse);

        setWorkspace({
          id: Number(workspaceId),
        });
      } catch (error) {
        console.error('Project loading failed:', error);

        setError(
          error.response?.data?.detail ||
            error.message ||
            'Failed to load project',
        );
      } finally {
        setLoading(false);
      }
    };

    loadProject();
  }, [workspaceId, projectId]);

  if (loading) {
    return (
      <div className='flex min-h-screen items-center justify-center bg-stone-50'>
        <div className='text-center'>
          <div className='mx-auto mb-4 h-9 w-9 animate-spin rounded-full border-4 border-stone-200 border-t-slate-700' />

          <p className='text-sm text-slate-500'>Loading project...</p>
        </div>
      </div>
    );
  }

  if (error || !project || !workspace) {
    return (
      <div className='flex min-h-screen items-center justify-center bg-stone-50 p-6'>
        <div className='w-full max-w-md rounded-2xl border border-red-200 bg-white p-6 shadow-sm'>
          <h2 className='text-lg font-semibold text-red-600'>Project Error</h2>

          <p className='mt-2 text-sm text-slate-600'>
            {error || 'Project could not be loaded'}
          </p>

          <button
            type='button'
            onClick={() => navigate('/workspace')}
            className='mt-5 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-slate-800'
          >
            Back to Workspaces
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className='min-h-screen bg-stone-50'>
      <div className='px-4 pt-5 sm:px-6 sm:pt-7 lg:px-8 lg:pt-8'>
        <div className='mx-auto flex w-full max-w-7xl items-center'>
          <button
            type='button'
            onClick={() =>
              navigate(
                `/workspaces/${workspace.id}/projects/${project.id}/datasets`,
              )
            }
            className='group inline-flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:border-slate-300 hover:bg-slate-50 hover:shadow-md active:translate-y-0'
          >
            <span className='transition-transform duration-300 group-hover:-translate-x-0.5'>
              ←
            </span>

            <span>Datasets</span>
          </button>
        </div>
      </div>

      <Dashboard project={project} workspace={workspace} />
    </div>
  );
}

export default ProjectDashboard;
