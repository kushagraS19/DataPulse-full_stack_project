import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { getCurrentUser } from '../services/user_service';
import { useAuth } from '../context/authContext';

function Profile() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [loggingOut, setLoggingOut] = useState(false);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        setLoading(true);
        setError('');

        const data = await getCurrentUser();

        setUser(data);
      } catch (error) {
        console.error('Failed to fetch user:', error);

        setError(error.response?.data?.detail || 'Failed to fetch user');
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  const handleLogout = async () => {
    if (loggingOut) {
      return;
    }

    try {
      setLoggingOut(true);

      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      navigate('/login', { replace: true });
    }
  };

  const getInitials = () => {
    if (!user?.name) {
      return 'U';
    }

    const parts = user.name.trim().split(/\s+/);

    if (parts.length === 1) {
      return parts[0].charAt(0).toUpperCase();
    }

    return (
      parts[0].charAt(0) + parts[parts.length - 1].charAt(0)
    ).toUpperCase();
  };

  if (loading) {
    return (
      <div className='min-h-screen bg-stone-50 px-4 py-6 sm:px-6 lg:px-8'>
        <div className='mx-auto max-w-4xl animate-pulse'>
          <div className='h-3 w-20 rounded-full bg-stone-200' />

          <div className='mt-4 h-9 w-40 rounded-xl bg-stone-200' />

          <div className='mt-8 grid gap-5 lg:grid-cols-[240px_1fr]'>
            <div className='h-64 rounded-3xl border border-stone-200 bg-white' />

            <div className='h-96 rounded-3xl border border-stone-200 bg-white' />
          </div>
        </div>
      </div>
    );
  }

  if (error || !user) {
    return (
      <div className='flex min-h-screen items-center justify-center bg-stone-50 px-5'>
        <div className='w-full max-w-md rounded-3xl border border-stone-200 bg-white p-7 text-center shadow-sm animate-[profileAppear_450ms_ease-out_both]'>
          <div className='mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-red-50 font-bold text-red-500'>
            !
          </div>

          <h1 className='mt-5 text-xl font-bold text-slate-950'>
            Profile unavailable
          </h1>

          <p className='mt-2 text-sm leading-6 text-slate-500'>
            {error || 'Unable to load your account information.'}
          </p>

          <button
            type='button'
            onClick={() => navigate('/workspace')}
            className='mt-6 rounded-xl bg-slate-950 px-5 py-2.5 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-0.5 hover:bg-slate-800 hover:shadow-lg'
          >
            Back to Workspace
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className='min-h-screen bg-stone-50'>
      <div className='mx-auto w-full max-w-5xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8 lg:py-10'>
        {/* Header */}
        <header className='animate-[profileAppear_500ms_cubic-bezier(.22,1,.36,1)_both]'>
          <div className='flex items-center gap-2'>
            <span className='h-1.5 w-1.5 rounded-full bg-slate-900' />

            <span className='text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400'>
              Account settings
            </span>
          </div>

          <h1 className='mt-3 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl'>
            Profile
          </h1>

          <p className='mt-2 text-sm text-slate-500'>
            Your account information and session settings.
          </p>
        </header>

        {/* Main layout */}
        <div className='mt-8 grid gap-5 lg:grid-cols-[240px_minmax(0,1fr)]'>
          {/* Identity card */}
          <aside className='h-fit overflow-hidden rounded-3xl border border-stone-200 bg-white shadow-sm animate-[profileSlideLeft_550ms_cubic-bezier(.22,1,.36,1)_both]'>
            <div className='p-6'>
              {/* Avatar */}
              <div className='relative mx-auto flex h-24 w-24 items-center justify-center rounded-[1.75rem] bg-slate-950 text-2xl font-bold text-white shadow-xl shadow-slate-900/10'>
                {getInitials()}

                <span className='absolute -bottom-1.5 -right-1.5 flex h-7 w-7 items-center justify-center rounded-full border-4 border-white bg-emerald-500'>
                  <span className='h-2 w-2 rounded-full bg-white' />
                </span>
              </div>

              <div className='mt-5 text-center'>
                <h2 className='truncate text-lg font-bold text-slate-950'>
                  {user.name}
                </h2>

                <p className='mt-1 break-all text-xs leading-5 text-slate-400'>
                  {user.email}
                </p>
              </div>

              <div className='mt-6 border-t border-stone-100 pt-5'>
                <div className='flex items-center justify-between'>
                  <span className='text-xs font-medium text-slate-400'>
                    Status
                  </span>

                  <span className='flex items-center gap-1.5 text-xs font-semibold text-emerald-600'>
                    <span className='h-1.5 w-1.5 rounded-full bg-emerald-500' />
                    Active
                  </span>
                </div>

                <div className='mt-3 flex items-center justify-between'>
                  <span className='text-xs font-medium text-slate-400'>
                    User ID
                  </span>

                  <span className='font-mono text-xs font-semibold text-slate-700'>
                    #{user.id}
                  </span>
                </div>
              </div>
            </div>
          </aside>

          {/* Details */}
          <main className='min-w-0 space-y-5 animate-[profileSlideUp_600ms_cubic-bezier(.22,1,.36,1)_both]'>
            {/* Account overview */}
            <section className='rounded-3xl border border-stone-200 bg-white shadow-sm'>
              <div className='border-b border-stone-100 px-6 py-5 sm:px-7'>
                <div className='flex items-center justify-between gap-4'>
                  <div>
                    <h3 className='text-base font-bold text-slate-950'>
                      Account information
                    </h3>

                    <p className='mt-1 text-xs text-slate-400'>
                      Basic information associated with your account.
                    </p>
                  </div>

                  <div className='hidden h-9 w-9 items-center justify-center rounded-xl bg-stone-100 text-sm text-slate-500 sm:flex'>
                    ◎
                  </div>
                </div>
              </div>

              <div className='divide-y divide-stone-100'>
                {/* Name */}
                <div className='group flex flex-col gap-3 px-6 py-5 transition-colors duration-200 hover:bg-stone-50/70 sm:flex-row sm:items-center sm:justify-between sm:px-7'>
                  <div className='flex items-center gap-3'>
                    <div className='flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-stone-100 text-xs font-bold text-slate-600 transition-all duration-300 group-hover:bg-slate-950 group-hover:text-white'>
                      A
                    </div>

                    <div>
                      <p className='text-xs font-medium text-slate-400'>
                        Full name
                      </p>

                      <p className='mt-1 text-sm font-semibold text-slate-900'>
                        {user.name}
                      </p>
                    </div>
                  </div>

                  <span className='text-[10px] font-semibold uppercase tracking-wider text-slate-300'>
                    Account
                  </span>
                </div>

                {/* Email */}
                <div className='group flex flex-col gap-3 px-6 py-5 transition-colors duration-200 hover:bg-stone-50/70 sm:flex-row sm:items-center sm:justify-between sm:px-7'>
                  <div className='flex min-w-0 items-center gap-3'>
                    <div className='flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-stone-100 text-xs font-bold text-slate-600 transition-all duration-300 group-hover:bg-slate-950 group-hover:text-white'>
                      @
                    </div>

                    <div className='min-w-0'>
                      <p className='text-xs font-medium text-slate-400'>
                        Email address
                      </p>

                      <p className='mt-1 break-all text-sm font-semibold text-slate-900'>
                        {user.email}
                      </p>
                    </div>
                  </div>

                  <span className='flex shrink-0 items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-emerald-500'>
                    <span className='h-1.5 w-1.5 rounded-full bg-emerald-500' />
                    Verified
                  </span>
                </div>

                {/* ID */}
                <div className='group flex flex-col gap-3 px-6 py-5 transition-colors duration-200 hover:bg-stone-50/70 sm:flex-row sm:items-center sm:justify-between sm:px-7'>
                  <div className='flex items-center gap-3'>
                    <div className='flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-stone-100 text-xs font-bold text-slate-600 transition-all duration-300 group-hover:bg-slate-950 group-hover:text-white'>
                      #
                    </div>

                    <div>
                      <p className='text-xs font-medium text-slate-400'>
                        Account ID
                      </p>

                      <p className='mt-1 font-mono text-sm font-semibold text-slate-900'>
                        {user.id}
                      </p>
                    </div>
                  </div>

                  <span className='text-[10px] font-semibold uppercase tracking-wider text-slate-300'>
                    Internal ID
                  </span>
                </div>
              </div>
            </section>

            {/* Security */}
            <section className='rounded-3xl border border-stone-200 bg-white shadow-sm'>
              <div className='border-b border-stone-100 px-6 py-5 sm:px-7'>
                <h3 className='text-base font-bold text-slate-950'>Security</h3>

                <p className='mt-1 text-xs text-slate-400'>
                  Keep your account protected.
                </p>
              </div>

              <div className='p-6 sm:p-7'>
                <div className='flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between'>
                  <div className='flex items-start gap-3'>
                    <div className='flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-sm text-emerald-600'>
                      ✓
                    </div>

                    <div>
                      <p className='text-sm font-semibold text-slate-900'>
                        Account security
                      </p>

                      <p className='mt-1 max-w-lg text-xs leading-5 text-slate-400'>
                        Your account session is protected by DataPulse
                        authentication.
                      </p>
                    </div>
                  </div>

                  <span className='inline-flex shrink-0 items-center rounded-full bg-emerald-50 px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-emerald-600'>
                    Secure
                  </span>
                </div>
              </div>
            </section>

            {/* Danger / session area */}
            <section className='rounded-3xl border border-stone-200 bg-white shadow-sm'>
              <div className='px-6 py-5 sm:px-7'>
                <div className='flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between'>
                  <div>
                    <h3 className='text-sm font-bold text-slate-950'>
                      Current session
                    </h3>

                    <p className='mt-1 text-xs leading-5 text-slate-400'>
                      Signing out will end your current DataPulse session on
                      this device.
                    </p>
                  </div>

                  <button
                    type='button'
                    onClick={handleLogout}
                    disabled={loggingOut}
                    className='min-h-10 shrink-0 rounded-xl border border-stone-200 px-4 text-xs font-semibold text-slate-600 transition-all duration-300 hover:border-red-200 hover:bg-red-50 hover:text-red-600 disabled:cursor-not-allowed disabled:opacity-50'
                  >
                    {loggingOut ? 'Signing out...' : 'Sign out'}
                  </button>
                </div>
              </div>
            </section>
          </main>
        </div>
      </div>

      <style>{`
        @keyframes profileAppear {
          from {
            opacity: 0;
            transform: translateY(12px);
          }

          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes profileSlideLeft {
          from {
            opacity: 0;
            transform: translateX(-14px);
          }

          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        @keyframes profileSlideUp {
          from {
            opacity: 0;
            transform: translateY(18px);
          }

          to {
            opacity: 1;
            transform: translateY(0);
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

export default Profile;
