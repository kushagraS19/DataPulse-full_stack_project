import { useState } from 'react';
import { NavLink, useLocation, useNavigate, useParams } from 'react-router-dom';

import authApi from '../api/auth_api';

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { workspaceId, projectId } = useParams();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  const isProjectRoute =
    Boolean(workspaceId) &&
    Boolean(projectId) &&
    location.pathname.includes('/projects/');

  const closeMobile = () => {
    setMobileOpen(false);
  };

  const handleLogout = async () => {
    try {
      setLoggingOut(true);

      try {
        await authApi.post('/auth/logout');
      } catch (error) {
        console.error('Logout API failed:', error);
      }

      localStorage.removeItem('access_token');

      navigate('/login', { replace: true });
    } finally {
      setLoggingOut(false);
    }
  };

  const navItemClass = ({ isActive }) =>
    `group flex min-h-11 items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium transition-all duration-200 ${
      isActive
        ? 'bg-slate-900 text-white shadow-sm'
        : 'text-slate-600 hover:bg-stone-100 hover:text-slate-900'
    }`;

  const projectNavItemClass = ({ isActive }) =>
    `group flex min-h-10 items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200 ${
      isActive
        ? 'bg-slate-100 text-slate-950'
        : 'text-slate-500 hover:bg-stone-100 hover:text-slate-800'
    }`;

  const sidebarContent = (
    <div className='flex h-full min-h-screen flex-col border-r border-stone-200 bg-white'>
      {/* Brand */}
      <div className='flex h-20 items-center border-b border-stone-100 px-5'>
        <button
          type='button'
          onClick={() => {
            closeMobile();
            navigate('/home');
          }}
          className='group flex items-center gap-3'
        >
          <div className='flex h-9 w-9 items-center justify-center rounded-xl bg-slate-900 text-sm font-bold text-white shadow-sm transition-transform duration-200 group-hover:scale-105'>
            D
          </div>

          <div className='text-left'>
            <p className='text-base font-bold tracking-tight text-slate-950'>
              DataPulse
            </p>

            <p className='text-[11px] font-medium uppercase tracking-[0.14em] text-slate-400'>
              Analytics
            </p>
          </div>
        </button>
      </div>

      {/* Navigation */}
      <div className='flex-1 overflow-y-auto px-3 py-5'>
        <p className='mb-2 px-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400'>
          Workspace
        </p>

        <nav className='space-y-1'>
          <NavLink to='/home' className={navItemClass} onClick={closeMobile}>
            <span className='text-base'>⌂</span>
            <span>Home</span>
          </NavLink>

          <NavLink
            to='/workspace'
            className={navItemClass}
            onClick={closeMobile}
          >
            <span className='text-base'>▣</span>
            <span>Workspaces</span>
          </NavLink>
        </nav>

        {/* Project navigation */}
        {isProjectRoute && (
          <div className='mt-7'>
            <p className='mb-2 px-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400'>
              Current Project
            </p>

            <nav className='space-y-1'>
              <NavLink
                to={`/workspaces/${workspaceId}/projects/${projectId}`}
                end
                className={projectNavItemClass}
                onClick={closeMobile}
              >
                <span>▦</span>
                <span>Dashboard</span>
              </NavLink>

              <NavLink
                to={`/workspaces/${workspaceId}/projects/${projectId}/datasets`}
                className={projectNavItemClass}
                onClick={closeMobile}
              >
                <span>◫</span>
                <span>Datasets</span>
              </NavLink>
            </nav>
          </div>
        )}

        {/* Account */}
        <div className='mt-7'>
          <p className='mb-2 px-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400'>
            Account
          </p>

          <nav>
            <NavLink
              to='/profile'
              className={navItemClass}
              onClick={closeMobile}
            >
              <span className='text-base'>◎</span>
              <span>Profile</span>
            </NavLink>
          </nav>
        </div>
      </div>

      {/* Logout */}
      <div className='border-t border-stone-100 p-3'>
        <button
          type='button'
          onClick={handleLogout}
          disabled={loggingOut}
          className='flex min-h-11 w-full items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium text-slate-500 transition-all duration-200 hover:bg-rose-50 hover:text-rose-600 disabled:cursor-not-allowed disabled:opacity-60'
        >
          <span>↪</span>
          <span>{loggingOut ? 'Logging out...' : 'Logout'}</span>
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile header */}
      <div className='sticky top-0 z-40 flex h-16 items-center justify-between border-b border-stone-200 bg-white/95 px-4 backdrop-blur-md lg:hidden'>
        <button
          type='button'
          onClick={() => navigate('/workspace')}
          className='flex items-center gap-2.5'
        >
          <div className='flex h-8 w-8 items-center justify-center rounded-lg bg-slate-900 text-xs font-bold text-white'>
            D
          </div>

          <span className='font-bold tracking-tight text-slate-950'>
            DataPulse
          </span>
        </button>

        <button
          type='button'
          onClick={() => setMobileOpen((value) => !value)}
          aria-label='Toggle navigation'
          className='flex h-10 w-10 items-center justify-center rounded-xl border border-stone-200 text-lg text-slate-700 transition hover:bg-stone-50'
        >
          {mobileOpen ? '×' : '☰'}
        </button>
      </div>

      {/* Desktop sidebar */}
      <aside className='fixed inset-y-0 left-0 z-40 hidden w-64 lg:block'>
        {sidebarContent}
      </aside>

      {/* Mobile sidebar */}
      {mobileOpen && (
        <>
          <button
            type='button'
            aria-label='Close navigation'
            onClick={closeMobile}
            className='fixed inset-0 z-40 bg-slate-950/30 backdrop-blur-sm lg:hidden'
          />

          <aside className='fixed inset-y-0 left-0 z-50 w-[min(82vw,20rem)] shadow-2xl lg:hidden'>
            {sidebarContent}
          </aside>
        </>
      )}
    </>
  );
}

export default Sidebar;
