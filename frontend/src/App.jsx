import { BrowserRouter, Routes, Route } from 'react-router-dom';

import ProtectedRoute from './components/ProtectedRoute';
import AuthenticatedLayout from './components/AuthenticatedLayout';

import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Home from './pages/Home';
import Profile from './pages/profile';
import Workspace from './pages/Workspace';
import ProjectDashboard from './pages/ProjectDashboard';
import Datasets from './pages/Datasets';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path='/' element={<Landing />} />
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
          <Route path='/home' element={<Home />} />

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

          <Route
            path='/workspaces/:workspaceId/projects/:projectId/datasets/:datasetId/dashboard'
            element={<ProjectDashboard />}
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
