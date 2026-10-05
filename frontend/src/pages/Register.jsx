import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { registerUser } from '../services/auth_service';
import authApi from '../api/auth_api';

function Register() {
  const navigate = useNavigate();

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

  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value,
    });

    setMessage('');
    setError('');
  };

  const handleRegister = async (event) => {
    event.preventDefault();

    setMessage('');
    setError('');

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

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

    if (!otp.trim()) {
      setError('Please enter the verification OTP.');
      return;
    }

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
        <div className='absolute -left-32 -top-32 h-80 w-80 animate-[registerFloatOne_12s_ease-in-out_infinite] rounded-full bg-slate-300/25 blur-3xl' />

        <div className='absolute -bottom-40 -right-32 h-96 w-96 animate-[registerFloatTwo_15s_ease-in-out_infinite] rounded-full bg-stone-300/35 blur-3xl' />

        <div className='absolute left-[45%] top-[18%] h-40 w-40 animate-[registerFloatThree_10s_ease-in-out_infinite] rounded-full bg-slate-200/25 blur-3xl' />

        <div
          className='absolute inset-0 opacity-[0.035]'
          style={{
            backgroundImage:
              'linear-gradient(#0f172a 1px, transparent 1px), linear-gradient(90deg, #0f172a 1px, transparent 1px)',
            backgroundSize: '44px 44px',
          }}
        />
      </div>

      <div className='relative z-10 flex min-h-screen items-center justify-center px-4 py-8 sm:px-6'>
        <div className='grid w-full max-w-5xl overflow-hidden rounded-[2rem] border border-white/70 bg-white/75 shadow-[0_30px_100px_rgba(15,23,42,0.12)] backdrop-blur-2xl lg:grid-cols-[0.9fr_1.1fr]'>
          {/* Brand panel */}
          <div className='relative hidden overflow-hidden bg-slate-950 p-10 text-white lg:flex lg:min-h-[700px] lg:flex-col lg:justify-between'>
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
                  Start analyzing
                </p>

                <h1 className='mt-5 text-4xl font-bold leading-[1.08] tracking-tight text-white xl:text-5xl'>
                  Build your
                  <span className='mt-1 block text-slate-400'>
                    analytics workspace.
                  </span>
                </h1>

                <p className='mt-6 text-sm leading-7 text-slate-400'>
                  Create an account, verify your email, and start turning raw
                  datasets into useful insights.
                </p>
              </div>
            </div>

            {/* Progress indicator */}
            <div className='relative z-10'>
              <div className='flex items-center gap-3'>
                <div
                  className={`flex h-9 w-9 items-center justify-center rounded-full text-xs font-bold transition-all duration-500 ${
                    step === 'register'
                      ? 'bg-white text-slate-950'
                      : 'bg-white text-slate-950'
                  }`}
                >
                  {step === 'verified' ? '✓' : '1'}
                </div>

                <div className='h-px flex-1 bg-white/10'>
                  <div
                    className={`h-full bg-white transition-all duration-700 ${
                      step === 'register' ? 'w-0' : 'w-full'
                    }`}
                  />
                </div>

                <div
                  className={`flex h-9 w-9 items-center justify-center rounded-full text-xs font-bold transition-all duration-500 ${
                    step === 'register'
                      ? 'border border-white/15 text-slate-500'
                      : 'bg-white text-slate-950'
                  }`}
                >
                  {step === 'verified' ? '✓' : '2'}
                </div>
              </div>

              <div className='mt-3 flex justify-between text-[10px] font-bold uppercase tracking-wider text-slate-600'>
                <span>Account</span>
                <span>Verification</span>
              </div>
            </div>
          </div>

          {/* Form panel */}
          <div className='flex min-h-[620px] items-center justify-center p-6 sm:p-10 lg:p-12'>
            <div
              key={step}
              className='w-full max-w-md animate-[registerCardIn_500ms_cubic-bezier(.22,1,.36,1)_both]'
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

              {/* Registration */}
              {step === 'register' && (
                <>
                  <div className='mb-8'>
                    <p className='text-xs font-bold uppercase tracking-[0.18em] text-slate-400'>
                      Get started
                    </p>

                    <h2 className='mt-2 text-3xl font-bold tracking-tight text-slate-950'>
                      Create your account
                    </h2>

                    <p className='mt-2 text-sm leading-6 text-slate-500'>
                      Set up your DataPulse account and start analyzing your
                      data.
                    </p>
                  </div>

                  <form onSubmit={handleRegister} className='space-y-5'>
                    <div>
                      <label
                        htmlFor='register-name'
                        className='mb-2 block text-xs font-bold uppercase tracking-wider text-slate-600'
                      >
                        Full name
                      </label>

                      <input
                        id='register-name'
                        type='text'
                        name='name'
                        autoComplete='name'
                        value={formData.name}
                        onChange={handleChange}
                        placeholder='Your name'
                        required
                        className={inputClass}
                      />
                    </div>

                    <div>
                      <label
                        htmlFor='register-email'
                        className='mb-2 block text-xs font-bold uppercase tracking-wider text-slate-600'
                      >
                        Email
                      </label>

                      <input
                        id='register-email'
                        type='email'
                        name='email'
                        autoComplete='email'
                        value={formData.email}
                        onChange={handleChange}
                        placeholder='you@example.com'
                        required
                        className={inputClass}
                      />
                    </div>

                    <div>
                      <label
                        htmlFor='register-password'
                        className='mb-2 block text-xs font-bold uppercase tracking-wider text-slate-600'
                      >
                        Password
                      </label>

                      <div className='relative'>
                        <input
                          id='register-password'
                          type={showPassword ? 'text' : 'password'}
                          name='password'
                          autoComplete='new-password'
                          value={formData.password}
                          onChange={handleChange}
                          placeholder='At least 8 characters'
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

                      <p className='mt-2 text-xs text-slate-400'>
                        Use at least 8 characters for your password.
                      </p>
                    </div>

                    {message && (
                      <div className='animate-[registerMessageIn_350ms_ease-out_both] rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700'>
                        {message}
                      </div>
                    )}

                    {error && (
                      <div className='animate-[registerErrorShake_400ms_ease-out_both] rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700'>
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
                          Creating account...
                        </span>
                      ) : (
                        <span className='relative flex items-center gap-2'>
                          Create account
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
                      Already registered?
                    </span>

                    <div className='h-px flex-1 bg-stone-200' />
                  </div>

                  <button
                    type='button'
                    onClick={() => navigate('/login')}
                    className='h-12 w-full rounded-xl border border-stone-200 bg-white text-sm font-semibold text-slate-700 transition-all duration-300 hover:-translate-y-0.5 hover:border-slate-300 hover:bg-stone-50 hover:text-slate-950 hover:shadow-sm active:translate-y-0'
                  >
                    Back to login
                  </button>
                </>
              )}

              {/* Email verification */}
              {step === 'verify' && (
                <>
                  <button
                    type='button'
                    onClick={() => setStep('register')}
                    className='mb-7 inline-flex items-center gap-2 text-sm font-semibold text-slate-500 transition-colors duration-200 hover:text-slate-950'
                  >
                    <span className='transition-transform duration-200 hover:-translate-x-1'>
                      ←
                    </span>
                    Back to registration
                  </button>

                  <div className='mb-8'>
                    <div className='flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-950 text-lg text-white shadow-lg'>
                      @
                    </div>

                    <p className='mt-6 text-xs font-bold uppercase tracking-[0.18em] text-slate-400'>
                      Verify your account
                    </p>

                    <h2 className='mt-2 text-3xl font-bold tracking-tight text-slate-950'>
                      Check your email
                    </h2>

                    <p className='mt-3 text-sm leading-6 text-slate-500'>
                      We sent a verification OTP to
                      <strong className='break-all text-slate-800'>
                        {' '}
                        {formData.email}
                      </strong>
                      .
                    </p>
                  </div>

                  <form onSubmit={handleVerifyEmail} className='space-y-5'>
                    <div>
                      <label
                        htmlFor='verification-otp'
                        className='mb-2 block text-xs font-bold uppercase tracking-wider text-slate-600'
                      >
                        Verification OTP
                      </label>

                      <input
                        id='verification-otp'
                        type='text'
                        name='otp'
                        inputMode='numeric'
                        autoComplete='one-time-code'
                        maxLength={6}
                        value={otp}
                        onChange={(event) => {
                          setOtp(event.target.value.replace(/\D/g, ''));
                          setError('');
                          setMessage('');
                        }}
                        placeholder='Enter 6-digit OTP'
                        required
                        className={`${inputClass} text-center text-lg font-bold tracking-[0.4em]`}
                      />
                    </div>

                    {message && (
                      <div className='animate-[registerMessageIn_350ms_ease-out_both] rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700'>
                        {message}
                      </div>
                    )}

                    {error && (
                      <div className='animate-[registerErrorShake_400ms_ease-out_both] rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700'>
                        {error}
                      </div>
                    )}

                    <button
                      type='submit'
                      disabled={loading || otp.length === 0}
                      className={primaryButtonClass}
                    >
                      <span className='absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/10 to-transparent transition-transform duration-700 group-hover:translate-x-full' />

                      {loading ? (
                        <span className='relative flex items-center gap-2'>
                          <span className='h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white' />
                          Verifying...
                        </span>
                      ) : (
                        <span className='relative flex items-center gap-2'>
                          Verify email
                          <span className='transition-transform duration-200 group-hover:translate-x-1'>
                            →
                          </span>
                        </span>
                      )}
                    </button>

                    <button
                      type='button'
                      onClick={handleResendOtp}
                      disabled={loading}
                      className='h-11 w-full rounded-xl text-sm font-semibold text-slate-500 transition-all duration-200 hover:bg-stone-100 hover:text-slate-900 disabled:cursor-not-allowed disabled:opacity-50'
                    >
                      {loading ? 'Sending...' : 'Resend OTP'}
                    </button>
                  </form>
                </>
              )}

              {/* Verified */}
              {step === 'verified' && (
                <div className='text-center'>
                  <div className='mx-auto flex h-16 w-16 animate-[verifiedPop_550ms_cubic-bezier(.22,1,.36,1)_both] items-center justify-center rounded-2xl bg-emerald-500 text-2xl font-bold text-white shadow-xl shadow-emerald-500/20'>
                    ✓
                  </div>

                  <p className='mt-7 text-xs font-bold uppercase tracking-[0.18em] text-slate-400'>
                    Account verified
                  </p>

                  <h2 className='mt-2 text-3xl font-bold tracking-tight text-slate-950'>
                    You're all set.
                  </h2>

                  <p className='mx-auto mt-3 max-w-sm text-sm leading-6 text-slate-500'>
                    Your email has been verified successfully. You can now sign
                    in and start using DataPulse.
                  </p>

                  {message && (
                    <div className='mt-6 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700'>
                      {message}
                    </div>
                  )}

                  <button
                    type='button'
                    onClick={() => navigate('/login')}
                    className='group mt-7 flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-slate-950 text-sm font-semibold text-white shadow-lg shadow-slate-900/10 transition-all duration-300 hover:-translate-y-0.5 hover:bg-slate-800 hover:shadow-xl active:translate-y-0'
                  >
                    Continue to login
                    <span className='transition-transform duration-200 group-hover:translate-x-1'>
                      →
                    </span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes registerCardIn {
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

        @keyframes registerMessageIn {
          0% {
            opacity: 0;
            transform: translateY(-6px);
          }

          100% {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes registerErrorShake {
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

        @keyframes verifiedPop {
          0% {
            opacity: 0;
            transform: scale(0.5);
          }

          70% {
            transform: scale(1.08);
          }

          100% {
            opacity: 1;
            transform: scale(1);
          }
        }

        @keyframes registerFloatOne {
          0%,
          100% {
            transform: translate3d(0, 0, 0) scale(1);
          }

          50% {
            transform: translate3d(50px, 35px, 0) scale(1.08);
          }
        }

        @keyframes registerFloatTwo {
          0%,
          100% {
            transform: translate3d(0, 0, 0) scale(1);
          }

          50% {
            transform: translate3d(-45px, -30px, 0) scale(1.06);
          }
        }

        @keyframes registerFloatThree {
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

export default Register;
