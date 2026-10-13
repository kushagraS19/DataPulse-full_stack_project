import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/authContext';

function ProtectedRoute({ children, adminOnly = false }) {
  const { accessToken, user, authLoading } = useAuth();

  if (!accessToken) {
    return <Navigate to='/login' replace />;
  }

  if (authLoading) {
    return <div className='p-6'>Loading...</div>;
  }

  if (!user) {
    return <Navigate to='/login' replace />;
  }

  if (adminOnly && user.role !== 'admin') {
    return <Navigate to='/home' replace />;
  }

  return children;
}

export default ProtectedRoute;
