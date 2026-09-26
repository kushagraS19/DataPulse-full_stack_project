import { createContext, useContext, useState } from 'react';
import { logoutUser } from '../services/auth_service';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [accessToken, setAccessToken] = useState(
    localStorage.getItem('access_token'),
  );

  const login = (token) => {
    localStorage.setItem('access_token', token);
    setAccessToken(token);
  };

  const logout = async () => {
    try {
      await logoutUser();
    } finally {
      localStorage.removeItem('access_token');
      setAccessToken(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        accessToken,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
};
