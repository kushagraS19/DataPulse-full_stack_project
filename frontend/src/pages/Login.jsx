import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { loginUser } from '../services/auth_service';
import { useAuth } from '../context/authContext';
import authApi from '../api/auth_api';

function Login() {
  const navigate = useNavigate();
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

  const [showPassword, setShowPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);

  const handleLoginChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value,
    });

    setError('');
    setMessage('');
  };

  const handleResetChange = (event) => {
    setResetData({
      ...resetData,
      [event.target.name]: event.target.value,
    });

    setError('');
    setMessage('');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setMessage('');
    setError('');
    setLoading(true);

    try {
      const data = await loginUser(formData);

      login(data.access_token);

      navigate('/home', { replace: true });
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

    if (resetData.new_password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

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

    setResetData({
      email: formData.email,
      otp: '',
      new_password: '',
    });
  };

  const inputClass =
    'h-12 w-full rounded-xl border border-stone-200 bg-stone-50/80 px-4 text-sm text-slate-900 outline-none transition-all duration-300 placeholder:text-slate-400 hover:border-stone-300 hover:bg-white focus:border-slate-500 focus:bg-white focus:ring-4 focus:ring-slate-900/5';

  const passwordInputClass =
    'h-12 w-full rounded-xl border border-stone-200 bg-stone-50/80 px-4 pr-12 text-sm text-slate-900 outline-none transition-all duration-300 placeholder:text-slate-400 hover:border-stone-300 hover:bg-white focus:border-slate-500 focus:bg-white focus:ring-4 focus:ring-slate-900/5';

  const primaryButtonClass =
    'group relative flex h-12 w-full items-center justify-center overflow-hidden rounded-xl bg-slate-950 text-sm font-semibold text-white shadow-lg shadow-slate-900/10 transition-all duration-300 hover:-translate-y-0.5 hover:bg-slate-800 hover:shadow-xl hover:shadow-slate-900/15 active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0';

  return (
    <div className='relative min-h-screen overflow-hidden bg-[#f5f3ef]'>
      {/* Ambient background */}
      <div className='pointer-events-none absolute inset-0 overflow-hidden'>
        <div className='absolute -left-32 -top-32 h-80 w-80 animate-[floatOne_12s_ease-in-out_infinite] rounded-full bg-slate-300/25 blur-3xl' />

        <div className='absolute -bottom-40 -right-32 h-96 w-96 animate-[floatTwo_15s_ease-in-out_infinite] rounded-full bg-stone-300/35 blur-3xl' />

        <div className='absolute left-[45%] top-[18%] h-40 w-40 animate-[floatThree_10s_ease-in-out_infinite] rounded-full bg-slate-200/25 blur-3xl' />

        <div
          className='absolute inset-0 opacity-[0.035]'
          style={{
            backgroundImage:
              'linear-gradient(#0f172a 1px, transparent 1px), linear-gradient(90deg, #0f172a 1px, transparent 1px)',
            backgroundSize: '44px 44px',
          }}
        />
      </div>

      {/* Main layout */}
      <div className='relative z-10 flex min-h-screen items-center justify-center px-4 py-8 sm:px-6'>
        <div className='grid w-full max-w-5xl overflow-hidden rounded-[2rem] border border-white/70 bg-white/75 shadow-[0_30px_100px_rgba(15,23,42,0.12)] backdrop-blur-2xl lg:grid-cols-[0.9fr_1.1fr]'>
          {/* Brand panel */}
          <div className='relative hidden overflow-hidden bg-slate-950 p-10 text-white lg:flex lg:min-h-[680px] lg:flex-col lg:justify-between'>
            <div className='absolute -right-24 -top-24 h-64 w-64 rounded-full border border-white/10 bg-white/[0.03]' />
            <div className='absolute -bottom-32 -left-20 h-72 w-72 rounded-full border border-white/10 bg-white/[0.03]' />

            <div className='relative z-10'>
              <div className='flex items-center gap-3'>
                <div className='flex h-10 w-10 items-center justify-center rounded-xl bg-white text-sm font-black text-slate-950 shadow-lg'>
                  D
                </div>

                <div>
                  <p className='text-base font-bold tracking-tight'>
                    DataPulse
                  </p>

                  <p className='text-[10px] font-medium uppercase tracking-[0.18em] text-slate-400'>
                    Analytics
                  </p>
                </div>
              </div>

              <div className='mt-20 max-w-sm'>
                <p className='text-xs font-bold uppercase tracking-[0.2em] text-slate-500'>
                  Your data. Your pulse.
                </p>

                <h1 className='mt-5 text-4xl font-bold leading-[1.08] tracking-tight text-white xl:text-5xl'>
                  Turn raw data into
                  <span className='mt-1 block text-slate-400'>
                    useful decisions.
                  </span>
                </h1>

                <p className='mt-6 text-sm leading-7 text-slate-400'>
                  Upload your data, explore meaningful patterns, and understand
                  what your numbers are actually telling you.
                </p>
              </div>
            </div>

            <div className='relative z-10'>
              <div className='grid grid-cols-3 gap-2'>
                <div className='rounded-xl border border-white/10 bg-white/[0.04] p-3'>
                  <div className='h-1.5 w-8 rounded-full bg-white/60' />
                  <div className='mt-3 h-1.5 w-full rounded-full bg-white/10' />
                  <div className='mt-2 h-1.5 w-2/3 rounded-full bg-white/10' />
                </div>

                <div className='rounded-xl border border-white/10 bg-white/[0.04] p-3'>
                  <div className='flex items-end gap-1'>
                    <span className='h-5 w-1.5 rounded-full bg-white/30' />
                    <span className='h-8 w-1.5 rounded-full bg-white/50' />
                    <span className='h-6 w-1.5 rounded-full bg-white/40' />
                    <span className='h-10 w-1.5 rounded-full bg-white/70' />
                  </div>
                </div>

                <div className='rounded-xl border border-white/10 bg-white/[0.04] p-3'>
                  <div className='h-8 w-8 rounded-full border-2 border-white/20 border-t-white/70' />
                </div>
              </div>

              <p className='mt-5 text-[11px] text-slate-600'>
                Analytics workspace
              </p>
            </div>
          </div>

          {/* Form panel */}
          <div className='flex min-h-[620px] items-center justify-center p-6 sm:p-10 lg:p-12'>
            <div
              key={`${mode}-${resetStep}`}
              className='w-full max-w-md animate-[authCardIn_500ms_cubic-bezier(.22,1,.36,1)_both]'
            >
              {/* Mobile brand */}
              <div className='mb-9 flex items-center gap-3 lg:hidden'>
                <div className='flex h-10 w-10 items-center justify-center rounded-xl bg-slate-950 text-sm font-black text-white shadow-lg'>
                  D
                </div>

                <div>
                  <p className='text-base font-bold tracking-tight text-slate-950'>
                    DataPulse
                  </p>

                  <p className='text-[10px] font-medium uppercase tracking-[0.18em] text-slate-400'>
                    Analytics
                  </p>
                </div>
              </div>

              {/* Login */}
              {mode === 'login' && (
                <>
                  <div className='mb-8'>
                    <p className='text-xs font-bold uppercase tracking-[0.18em] text-slate-400'>
                      Welcome back
                    </p>

                    <h2 className='mt-2 text-3xl font-bold tracking-tight text-slate-950'>
                      Sign in to DataPulse
                    </h2>

                    <p className='mt-2 text-sm leading-6 text-slate-500'>
                      Continue to your analytics workspace.
                    </p>
                  </div>

                  <form onSubmit={handleSubmit} className='space-y-5'>
                    <div>
                      <label
                        htmlFor='login-email'
                        className='mb-2 block text-xs font-bold uppercase tracking-wider text-slate-600'
                      >
                        Email
                      </label>

                      <input
                        id='login-email'
                        type='email'
                        name='email'
                        autoComplete='email'
                        value={formData.email}
                        onChange={handleLoginChange}
                        placeholder='you@example.com'
                        required
                        className={inputClass}
                      />
                    </div>

                    <div>
                      <div className='mb-2 flex items-center justify-between'>
                        <label
                          htmlFor='login-password'
                          className='block text-xs font-bold uppercase tracking-wider text-slate-600'
                        >
                          Password
                        </label>

                        <button
                          type='button'
                          onClick={switchToForgotPassword}
                          className='text-xs font-semibold text-slate-500 transition-colors duration-200 hover:text-slate-950'
                        >
                          Forgot password?
                        </button>
                      </div>

                      <div className='relative'>
                        <input
                          id='login-password'
                          type={showPassword ? 'text' : 'password'}
                          name='password'
                          autoComplete='current-password'
                          value={formData.password}
                          onChange={handleLoginChange}
                          placeholder='Enter your password'
                          required
                          className={passwordInputClass}
                        />

                        <button
                          type='button'
                          onClick={() => setShowPassword((value) => !value)}
                          aria-label={
                            showPassword ? 'Hide password' : 'Show password'
                          }
                          className='absolute right-2 top-1/2 flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-lg text-xs font-bold text-slate-400 transition-all duration-200 hover:bg-stone-100 hover:text-slate-700'
                        >
                          {showPassword ? 'Hide' : 'Show'}
                        </button>
                      </div>
                    </div>

                    {message && (
                      <div className='animate-[messageIn_350ms_ease-out_both] rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700'>
                        {message}
                      </div>
                    )}

                    {error && (
                      <div className='animate-[errorShake_400ms_ease-out_both] rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700'>
                        {error}
                      </div>
                    )}

                    <button
                      type='submit'
                      disabled={loading}
                      className={primaryButtonClass}
                    >
                      <span className='absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/10 to-transparent transition-transform duration-700 group-hover:translate-x-full' />

                      {loading ? (
                        <span className='relative flex items-center gap-2'>
                          <span className='h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white' />
                          Signing in...
                        </span>
                      ) : (
                        <span className='relative flex items-center gap-2'>
                          Sign in
                          <span className='transition-transform duration-200 group-hover:translate-x-1'>
                            →
                          </span>
                        </span>
                      )}
                    </button>
                  </form>

                  <div className='my-7 flex items-center gap-3'>
                    <div className='h-px flex-1 bg-stone-200' />
                    <span className='text-[10px] font-bold uppercase tracking-widest text-slate-400'>
                      New here?
                    </span>
                    <div className='h-px flex-1 bg-stone-200' />
                  </div>

                  <button
                    type='button'
                    onClick={() => navigate('/register')}
                    className='h-12 w-full rounded-xl border border-stone-200 bg-white text-sm font-semibold text-slate-700 transition-all duration-300 hover:-translate-y-0.5 hover:border-slate-300 hover:bg-stone-50 hover:text-slate-950 hover:shadow-sm active:translate-y-0'
                  >
                    Create an account
                  </button>
                </>
              )}

              {/* Forgot password */}
              {mode === 'forgot' && (
                <>
                  <button
                    type='button'
                    onClick={switchToLogin}
                    className='mb-7 inline-flex items-center gap-2 text-sm font-semibold text-slate-500 transition-colors duration-200 hover:text-slate-950'
                  >
                    <span className='transition-transform duration-200 hover:-translate-x-1'>
                      ←
                    </span>
                    Back to login
                  </button>

                  <div className='mb-8'>
                    <div className='flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-950 text-lg text-white shadow-lg'>
                      {resetStep === 1 ? '↻' : '✓'}
                    </div>

                    <p className='mt-6 text-xs font-bold uppercase tracking-[0.18em] text-slate-400'>
                      {resetStep === 1
                        ? 'Account recovery'
                        : 'Verify your identity'}
                    </p>

                    <h2 className='mt-2 text-3xl font-bold tracking-tight text-slate-950'>
                      {resetStep === 1
                        ? 'Reset your password'
                        : 'Enter your OTP'}
                    </h2>

                    <p className='mt-2 text-sm leading-6 text-slate-500'>
                      {resetStep === 1
                        ? 'We will send a one-time code to your registered email.'
                        : 'Use the OTP sent to your email and choose a new password.'}
                    </p>
                  </div>

                  {resetStep === 1 ? (
                    <form onSubmit={handleRequestReset} className='space-y-5'>
                      <div>
                        <label
                          htmlFor='reset-email'
                          className='mb-2 block text-xs font-bold uppercase tracking-wider text-slate-600'
                        >
                          Email
                        </label>

                        <input
                          id='reset-email'
                          type='email'
                          name='email'
                          autoComplete='email'
                          value={resetData.email}
                          onChange={handleResetChange}
                          placeholder='you@example.com'
                          required
                          className={inputClass}
                        />
                      </div>

                      {message && (
                        <div className='animate-[messageIn_350ms_ease-out_both] rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700'>
                          {message}
                        </div>
                      )}

                      {error && (
                        <div className='animate-[errorShake_400ms_ease-out_both] rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700'>
                          {error}
                        </div>
                      )}

                      <button
                        type='submit'
                        disabled={loading}
                        className={primaryButtonClass}
                      >
                        <span className='absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/10 to-transparent transition-transform duration-700 group-hover:translate-x-full' />

                        {loading ? (
                          <span className='relative flex items-center gap-2'>
                            <span className='h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white' />
                            Sending OTP...
                          </span>
                        ) : (
                          <span className='relative flex items-center gap-2'>
                            Send OTP
                            <span className='transition-transform duration-200 group-hover:translate-x-1'>
                              →
                            </span>
                          </span>
                        )}
                      </button>
                    </form>
                  ) : (
                    <form onSubmit={handleResetPassword} className='space-y-5'>
                      <div>
                        <label
                          htmlFor='reset-email-verify'
                          className='mb-2 block text-xs font-bold uppercase tracking-wider text-slate-600'
                        >
                          Email
                        </label>

                        <input
                          id='reset-email-verify'
                          type='email'
                          name='email'
                          autoComplete='email'
                          value={resetData.email}
                          onChange={handleResetChange}
                          required
                          className={inputClass}
                        />
                      </div>

                      <div>
                        <label
                          htmlFor='reset-otp'
                          className='mb-2 block text-xs font-bold uppercase tracking-wider text-slate-600'
                        >
                          OTP
                        </label>

                        <input
                          id='reset-otp'
                          type='text'
                          name='otp'
                          inputMode='numeric'
                          autoComplete='one-time-code'
                          maxLength={6}
                          value={resetData.otp}
                          onChange={handleResetChange}
                          placeholder='Enter 6-digit OTP'
                          required
                          className={`${inputClass} text-center font-bold tracking-[0.35em]`}
                        />
                      </div>

                      <div>
                        <label
                          htmlFor='reset-new-password'
                          className='mb-2 block text-xs font-bold uppercase tracking-wider text-slate-600'
                        >
                          New Password
                        </label>

                        <div className='relative'>
                          <input
                            id='reset-new-password'
                            type={showNewPassword ? 'text' : 'password'}
                            name='new_password'
                            autoComplete='new-password'
                            value={resetData.new_password}
                            onChange={handleResetChange}
                            placeholder='At least 8 characters'
                            required
                            className={passwordInputClass}
                          />

                          <button
                            type='button'
                            onClick={() =>
                              setShowNewPassword((value) => !value)
                            }
                            aria-label={
                              showNewPassword
                                ? 'Hide new password'
                                : 'Show new password'
                            }
                            className='absolute right-2 top-1/2 flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-lg text-xs font-bold text-slate-400 transition-all duration-200 hover:bg-stone-100 hover:text-slate-700'
                          >
                            {showNewPassword ? 'Hide' : 'Show'}
                          </button>
                        </div>

                        <p className='mt-2 text-xs text-slate-400'>
                          Use at least 8 characters for your new password.
                        </p>
                      </div>

                      {message && (
                        <div className='animate-[messageIn_350ms_ease-out_both] rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700'>
                          {message}
                        </div>
                      )}

                      {error && (
                        <div className='animate-[errorShake_400ms_ease-out_both] rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700'>
                          {error}
                        </div>
                      )}

                      <button
                        type='submit'
                        disabled={loading}
                        className={primaryButtonClass}
                      >
                        <span className='absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/10 to-transparent transition-transform duration-700 group-hover:translate-x-full' />

                        {loading ? (
                          <span className='relative flex items-center gap-2'>
                            <span className='h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white' />
                            Resetting password...
                          </span>
                        ) : (
                          <span className='relative flex items-center gap-2'>
                            Reset password
                            <span className='transition-transform duration-200 group-hover:translate-x-1'>
                              →
                            </span>
                          </span>
                        )}
                      </button>

                      <button
                        type='button'
                        onClick={() => setResetStep(1)}
                        className='h-11 w-full rounded-xl text-sm font-semibold text-slate-500 transition-colors duration-200 hover:bg-stone-100 hover:text-slate-900'
                      >
                        Use a different email
                      </button>
                    </form>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes authCardIn {
          0% {
            opacity: 0;
            transform: translateY(18px) scale(0.985);
            filter: blur(5px);
          }

          100% {
            opacity: 1;
            transform: translateY(0) scale(1);
            filter: blur(0);
          }
        }

        @keyframes messageIn {
          0% {
            opacity: 0;
            transform: translateY(-6px);
          }

          100% {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes errorShake {
          0% {
            opacity: 0;
            transform: translateX(0);
          }

          25% {
            transform: translateX(-5px);
          }

          50% {
            transform: translateX(5px);
          }

          75% {
            transform: translateX(-3px);
          }

          100% {
            opacity: 1;
            transform: translateX(0);
          }
        }

        @keyframes floatOne {
          0%,
          100% {
            transform: translate3d(0, 0, 0) scale(1);
          }

          50% {
            transform: translate3d(50px, 35px, 0) scale(1.08);
          }
        }

        @keyframes floatTwo {
          0%,
          100% {
            transform: translate3d(0, 0, 0) scale(1);
          }

          50% {
            transform: translate3d(-45px, -30px, 0) scale(1.06);
          }
        }

        @keyframes floatThree {
          0%,
          100% {
            transform: translate3d(0, 0, 0);
          }

          50% {
            transform: translate3d(-25px, 35px, 0);
          }
        }

        @media (prefers-reduced-motion: reduce) {
          *,
          *::before,
          *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            scroll-behavior: auto !important;
            transition-duration: 0.01ms !important;
          }
        }
      `}</style>
    </div>
  );
}

export default Login;
