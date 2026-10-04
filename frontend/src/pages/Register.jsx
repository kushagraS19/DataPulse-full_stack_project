import { useState } from 'react';
import { registerUser } from '../services/auth_service';
import authApi from '../api/auth_api';

function Register() {
  const [step, setStep] = useState('register');

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
  });

  const [otp, setOtp] = useState('');

  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value,
    });
  };

  const handleRegister = async (event) => {
    event.preventDefault();

    setMessage('');
    setError('');
    setLoading(true);

    try {
      await registerUser(formData);

      setMessage(
        'Registration successful. Please check your email for the verification OTP.',
      );

      setStep('verify');
    } catch (error) {
      setError(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyEmail = async (event) => {
    event.preventDefault();

    setMessage('');
    setError('');
    setLoading(true);

    try {
      const response = await authApi.post('/auth/email-verification/verify', {
        email: formData.email,
        otp: otp,
      });

      setMessage(
        response.data.message ||
          'Email verified successfully. You can now login.',
      );

      setStep('verified');
    } catch (error) {
      setError(error.response?.data?.detail || 'Email verification failed');
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    setMessage('');
    setError('');
    setLoading(true);

    try {
      const response = await authApi.post('/auth/email-verification/request', {
        email: formData.email,
      });

      setMessage(
        response.data.message || 'Verification OTP sent successfully.',
      );
    } catch (error) {
      setError(
        error.response?.data?.detail || 'Unable to resend verification OTP',
      );
    } finally {
      setLoading(false);
    }
  };

  if (step === 'verify') {
    return (
      <div>
        <h1>Verify Your Email</h1>

        <p>
          We sent a verification OTP to <strong>{formData.email}</strong>.
        </p>

        <form onSubmit={handleVerifyEmail}>
          <div>
            <label>Verification OTP</label>

            <input
              type='text'
              name='otp'
              value={otp}
              onChange={(event) => setOtp(event.target.value)}
              required
            />
          </div>

          <button type='submit' disabled={loading}>
            {loading ? 'Verifying...' : 'Verify Email'}
          </button>
        </form>

        <button type='button' onClick={handleResendOtp} disabled={loading}>
          Resend OTP
        </button>

        {message && <p>{message}</p>}
        {error && <p>{error}</p>}
      </div>
    );
  }

  if (step === 'verified') {
    return (
      <div>
        <h1>Email Verified</h1>

        <p>
          Your email has been verified successfully. You can now login to
          DataPulse.
        </p>

        <a href='/login'>Go to Login</a>

        {message && <p>{message}</p>}
      </div>
    );
  }

  return (
    <div>
      <h1>Create Account</h1>

      <form onSubmit={handleRegister}>
        <div>
          <label>Name</label>

          <input
            type='text'
            name='name'
            value={formData.name}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label>Email</label>

          <input
            type='email'
            name='email'
            value={formData.email}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label>Password</label>

          <input
            type='password'
            name='password'
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>

        <button type='submit' disabled={loading}>
          {loading ? 'Creating Account...' : 'Register'}
        </button>
      </form>

      {message && <p>{message}</p>}
      {error && <p>{error}</p>}
    </div>
  );
}

export default Register;
