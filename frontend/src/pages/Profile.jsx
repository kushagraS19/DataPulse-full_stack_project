import { useEffect, useState } from 'react';
import { getCurrentUser } from '../services/user_service';
import { useAuth } from '../context/authContext';
import { useNavigate } from 'react-router-dom';

function Profile() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await getCurrentUser();
        setUser(data);
      } catch (error) {
        setError(error.response?.data?.detail || 'Failed to fetch user');
      }
    };

    fetchUser();
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      navigate('/login');
    }
  };

  return (
    <div>
      <h1>Profile</h1>

      {error && <p>{error}</p>}

      {user && (
        <div>
          <p>ID: {user.id}</p>
          <p>Name: {user.name}</p>
          <p>Email: {user.email}</p>

          <button onClick={handleLogout}>Logout</button>
        </div>
      )}
    </div>
  );
}

export default Profile;
