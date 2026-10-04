import { useState } from 'react';
import { loginUser } from '../services/auth_service';
import { useAuth } from '../context/authContext';
import authApi from '../api/auth_api';

function Login() {
  const { login } = useAuth();

  const [mode, setMode] = useState('login');

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const [resetData, setResetData] = useState({
    email: '',
    otp: '',
    new_password: '',
  });

  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [resetStep, setResetStep] = useState(1);
  const [loading, setLoading] = useState(false);

  const handleLoginChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value,
    });
  };

  const handleResetChange = (event) => {
    setResetData({
      ...resetData,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setMessage('');
    setError('');
    setLoading(true);

    try {
      const data = await loginUser(formData);

      login(data.access_token);

      setMessage('Login successful');
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRequestReset = async (event) => {
    event.preventDefault();

    setMessage('');
    setError('');
    setLoading(true);

    try {
      const response = await authApi.post('/auth/password-reset/request', {
        email: resetData.email,
      });

      setMessage(
        response.data.message ||
          'If an account exists for this email, an OTP has been sent.',
      );

      setResetStep(2);
    } catch (error) {
      setError(
        error.response?.data?.detail || 'Unable to request password reset',
      );
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (event) => {
    event.preventDefault();

    setMessage('');
    setError('');
    setLoading(true);

    try {
      const response = await authApi.post('/auth/password-reset/verify', {
        email: resetData.email,
        otp: resetData.otp,
        new_password: resetData.new_password,
      });

      setMessage(response.data.message || 'Password reset successfully');

      setResetData({
        email: '',
        otp: '',
        new_password: '',
      });

      setResetStep(1);
    } catch (error) {
      setError(error.response?.data?.detail || 'Unable to reset password');
    } finally {
      setLoading(false);
    }
  };

  const switchToLogin = () => {
    setMode('login');
    setResetStep(1);
    setMessage('');
    setError('');
  };

  const switchToForgotPassword = () => {
    setMode('forgot');
    setResetStep(1);
    setMessage('');
    setError('');
  };

  if (mode === 'forgot') {
    return (
      <div>
        <h1>Forgot Password</h1>

        {resetStep === 1 ? (
          <form onSubmit={handleRequestReset}>
            <div>
              <label>Email</label>

              <input
                type='email'
                name='email'
                value={resetData.email}
                onChange={handleResetChange}
                required
              />
            </div>

            <button type='submit' disabled={loading}>
              {loading ? 'Sending...' : 'Send OTP'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleResetPassword}>
            <div>
              <label>Email</label>

              <input
                type='email'
                name='email'
                value={resetData.email}
                onChange={handleResetChange}
                required
              />
            </div>

            <div>
              <label>OTP</label>

              <input
                type='text'
                name='otp'
                value={resetData.otp}
                onChange={handleResetChange}
                required
              />
            </div>

            <div>
              <label>New Password</label>

              <input
                type='password'
                name='new_password'
                value={resetData.new_password}
                onChange={handleResetChange}
                required
              />
            </div>

            <button type='submit' disabled={loading}>
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
        )}

        <button type='button' onClick={switchToLogin}>
          Back to Login
        </button>

        {message && <p>{message}</p>}
        {error && <p>{error}</p>}
      </div>
    );
  }

  return (
    <div>
      <h1>Login</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Email</label>

          <input
            type='email'
            name='email'
            value={formData.email}
            onChange={handleLoginChange}
            required
          />
        </div>

        <div>
          <label>Password</label>

          <input
            type='password'
            name='password'
            value={formData.password}
            onChange={handleLoginChange}
            required
          />
        </div>

        <button type='submit' disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>

      <button type='button' onClick={switchToForgotPassword}>
        Forgot Password?
      </button>

      {message && <p>{message}</p>}
      {error && <p>{error}</p>}
    </div>
  );
}

export default Login;
