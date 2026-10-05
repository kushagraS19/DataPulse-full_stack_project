import { BrowserRouter, Routes, Route } from 'react-router-dom';

import ProtectedRoute from './components/ProtectedRoute';
import AuthenticatedLayout from './components/AuthenticatedLayout';

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
        {/* Public routes */}
        <Route path='/login' element={<Login />} />
        <Route path='/register' element={<Register />} />

        {/* Protected application routes */}
        <Route
          element={
            <ProtectedRoute>
              <AuthenticatedLayout />
            </ProtectedRoute>
          }
        >
          <Route path='/profile' element={<Profile />} />

          <Route path='/workspace' element={<Workspace />} />

          <Route
            path='/workspaces/:workspaceId/projects/:projectId'
            element={<ProjectDashboard />}
          />

          <Route
            path='/workspaces/:workspaceId/projects/:projectId/datasets'
            element={<Datasets />}
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
