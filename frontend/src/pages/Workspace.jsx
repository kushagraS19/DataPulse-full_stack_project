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

  const loadWorkspaces = async () => {
    try {
      setLoading(true);
      setError('');

      const data = await getWorkspaces();

      setWorkspaces(data);

      if (data.length > 0) {
        setSelectedWorkspace(data[0]);
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

    if (!workspaceName.trim()) {
      return;
    }

    try {
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
    }
  };

  const handleCreateProject = async (event) => {
    event.preventDefault();

    if (!selectedWorkspace || !projectName.trim()) {
      return;
    }

    try {
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
    }
  };

  const handleProjectSelect = (project) => {
    navigate(`/workspaces/${selectedWorkspace.id}/projects/${project.id}`);
  };

  if (loading) {
    return <div>Loading workspaces...</div>;
  }

  return (
    <div>
      <h1>Workspaces</h1>

      {error && <p>{error}</p>}

      <form onSubmit={handleCreateWorkspace}>
        <input
          type='text'
          placeholder='Workspace name'
          value={workspaceName}
          onChange={(event) => setWorkspaceName(event.target.value)}
        />

        <button type='submit'>Create Workspace</button>
      </form>

      <hr />

      <div>
        <h2>Your Workspaces</h2>

        {workspaces.length === 0 ? (
          <p>No workspaces yet.</p>
        ) : (
          workspaces.map((workspace) => (
            <button
              key={workspace.id}
              type='button'
              onClick={() => setSelectedWorkspace(workspace)}
            >
              {workspace.name}
            </button>
          ))
        )}
      </div>

      {selectedWorkspace && (
        <div>
          <hr />

          <h2>{selectedWorkspace.name}</h2>

          <form onSubmit={handleCreateProject}>
            <input
              type='text'
              placeholder='Project name'
              value={projectName}
              onChange={(event) => setProjectName(event.target.value)}
            />

            <button type='submit'>Create Project</button>
          </form>

          {projectError && <p>{projectError}</p>}

          <h3>Projects</h3>

          {projectsLoading ? (
            <p>Loading projects...</p>
          ) : projects.length === 0 ? (
            <p>No projects yet.</p>
          ) : (
            <ul>
              {projects.map((project) => (
                <li key={project.id}>
                  <button
                    type='button'
                    onClick={() => handleProjectSelect(project)}
                  >
                    {project.name}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

export default Workspace;
