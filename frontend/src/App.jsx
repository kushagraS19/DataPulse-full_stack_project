import { BrowserRouter, Routes, Route } from 'react-router-dom';

import ProtectedRoute from './components/ProtectedRoute';

import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/profile';
import Workspace from './pages/Workspace';
import ProjectDashboard from './pages/ProjectDashboard';
import Datasets from './pages/Datasets';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path='/login' element={<Login />} />

        <Route path='/register' element={<Register />} />

        <Route
          path='/profile'
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />

        <Route
          path='/workspace'
          element={
            <ProtectedRoute>
              <Workspace />
            </ProtectedRoute>
          }
        />

        <Route
          path='/workspaces/:workspaceId/projects/:projectId'
          element={
            <ProtectedRoute>
              <ProjectDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path='/workspaces/:workspaceId/projects/:projectId/datasets'
          element={
            <ProtectedRoute>
              <Datasets />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
