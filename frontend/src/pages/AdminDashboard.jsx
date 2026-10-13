import { useCallback, useEffect, useState } from 'react';
import authApi from '../api/auth_api';
import { useAuth } from '../context/authContext';

const PAGE_SIZE = 10;

const initialOverview = {
  total_users: 0,
  verified_users: 0,
  unverified_users: 0,
  total_workspaces: 0,
  total_projects: 0,
  total_datasets: 0,
  total_dashboards: 0,
  total_charts: 0,
  total_rows: 0,
  storage_bytes: 0,
};

const formatNumber = (value = 0) =>
  new Intl.NumberFormat('en-IN').format(value);

const formatBytes = (bytes = 0) => {
  if (!bytes) return '0 B';

  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const index = Math.min(
    Math.floor(Math.log(bytes) / Math.log(1024)),
    units.length - 1,
  );

  return `${(bytes / 1024 ** index).toFixed(index === 0 ? 0 : 2)} ${units[index]}`;
};

const formatDate = (date) => {
  if (!date) return '—';

  const parsedDate = new Date(date);

  return Number.isNaN(parsedDate.getTime())
    ? '—'
    : parsedDate.toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
      });
};

function StatCard({ title, value, description }) {
  return (
    <div className='rounded-xl border border-slate-200 bg-white p-5 shadow-sm'>
      <p className='text-sm font-medium text-slate-500'>{title}</p>
      <p className='mt-3 text-2xl font-bold tracking-tight text-slate-900'>
        {value}
      </p>
      <p className='mt-2 text-xs text-slate-500'>{description}</p>
    </div>
  );
}

function StatusBadge({ active }) {
  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${
        active ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
      }`}
    >
      {active ? 'Active' : 'Deactivated'}
    </span>
  );
}

function VerificationBadge({ verified }) {
  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${
        verified ? 'bg-blue-50 text-blue-700' : 'bg-amber-50 text-amber-700'
      }`}
    >
      {verified ? 'Verified' : 'Unverified'}
    </span>
  );
}

function AdminDashboard() {
  const { user: currentUser } = useAuth();

  const [overview, setOverview] = useState(initialOverview);
  const [users, setUsers] = useState([]);
  const [totalUsers, setTotalUsers] = useState(0);
  const [auditLogs, setAuditLogs] = useState([]);

  const [searchInput, setSearchInput] = useState('');
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [page, setPage] = useState(0);

  const [loading, setLoading] = useState(true);
  const [actionUserId, setActionUserId] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Debounce the search input.
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearch(searchInput.trim());
      setPage(0);
    }, 350);

    return () => clearTimeout(timer);
  }, [searchInput]);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      const [overviewResponse, usersResponse, auditResponse] =
        await Promise.all([
          authApi.get('/users/admin/overview'),
          authApi.get('/users/admin/users', {
            params: {
              search: search || undefined,
              role: roleFilter || undefined,
              limit: PAGE_SIZE,
              offset: page * PAGE_SIZE,
            },
          }),
          authApi.get('/users/admin/audit-logs', {
            params: { limit: 10, offset: 0 },
          }),
        ]);

      setOverview(overviewResponse.data);
      setUsers(usersResponse.data.items);
      setTotalUsers(usersResponse.data.total);
      setAuditLogs(auditResponse.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Unable to load admin dashboard data.',
      );
    } finally {
      setLoading(false);
    }
  }, [search, roleFilter, page]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const performAction = async (userId, action, callback) => {
    setActionUserId(userId);
    setError('');
    setSuccess('');

    try {
      await callback();
      setSuccess(action);
      await loadData();
    } catch (err) {
      setError(
        err.response?.data?.detail || `Unable to ${action.toLowerCase()}.`,
      );
    } finally {
      setActionUserId(null);
    }
  };

  const handleStatusChange = (targetUser) => {
    if (targetUser.id === currentUser?.id) {
      setError('You cannot deactivate your own account.');
      return;
    }

    const newStatus = !targetUser.is_active;
    const action = newStatus ? 'Reactivate' : 'Deactivate';

    const confirmed = window.confirm(
      `${action} ${targetUser.name}'s account? ${
        newStatus
          ? 'The user will be able to sign in again.'
          : 'The user will lose access to authenticated endpoints.'
      }`,
    );

    if (!confirmed) return;

    performAction(
      targetUser.id,
      newStatus
        ? 'User account reactivated successfully'
        : 'User account deactivated successfully',
      () =>
        authApi.patch(`/users/admin/users/${targetUser.id}/status`, {
          is_active: newStatus,
        }),
    );
  };

  const handleDelete = (targetUser) => {
    if (targetUser.id === currentUser?.id) {
      setError('You cannot delete your own admin account.');
      return;
    }

    const confirmed = window.confirm(
      `Permanently delete ${targetUser.name} (${targetUser.email}) and their associated data? This action cannot be undone.`,
    );

    if (!confirmed) return;

    performAction(targetUser.id, 'User deleted successfully', () =>
      authApi.delete(`/users/admin-delete/${targetUser.id}`),
    );
  };

  const totalPages = Math.max(1, Math.ceil(totalUsers / PAGE_SIZE));

  const resourceColumns = [
    { key: 'workspace_count', label: 'Workspaces' },
    { key: 'project_count', label: 'Projects' },
    { key: 'dataset_count', label: 'Datasets' },
    { key: 'dashboard_count', label: 'Dashboards' },
    { key: 'chart_count', label: 'Charts' },
  ];

  return (
    <div className='min-h-screen bg-slate-50 text-slate-900'>
      <main className='mx-auto max-w-[1600px] px-4 py-8 sm:px-6 lg:px-8'>
        {/* Page header */}
        <div className='mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between'>
          <div>
            <p className='text-sm font-semibold uppercase tracking-wider text-blue-600'>
              DataPulse Administration
            </p>
            <h1 className='mt-2 text-3xl font-bold tracking-tight'>
              Admin Dashboard
            </h1>
            <p className='mt-2 text-sm text-slate-500'>
              Manage users, monitor platform usage, and control account access.
            </p>
          </div>

          <button
            type='button'
            onClick={loadData}
            disabled={loading}
            className='rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50'
          >
            {loading ? 'Refreshing...' : 'Refresh data'}
          </button>
        </div>

        {/* Notifications */}
        {error && (
          <div
            role='alert'
            className='mb-5 flex items-start justify-between gap-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700'
          >
            <span>{error}</span>
            <button
              type='button'
              onClick={() => setError('')}
              aria-label='Dismiss error'
              className='font-bold'
            >
              ×
            </button>
          </div>
        )}

        {success && (
          <div
            role='status'
            className='mb-5 flex items-start justify-between gap-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700'
          >
            <span>{success}</span>
            <button
              type='button'
              onClick={() => setSuccess('')}
              aria-label='Dismiss notification'
              className='font-bold'
            >
              ×
            </button>
          </div>
        )}

        {/* Platform overview */}
        <section>
          <div className='mb-4'>
            <h2 className='text-lg font-bold'>Platform overview</h2>
            <p className='mt-1 text-sm text-slate-500'>
              Current totals across your DataPulse installation.
            </p>
          </div>

          <div className='grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4'>
            <StatCard
              title='Total users'
              value={formatNumber(overview.total_users)}
              description={`${formatNumber(overview.verified_users)} verified`}
            />
            <StatCard
              title='Unverified users'
              value={formatNumber(overview.unverified_users)}
              description='Accounts awaiting email verification'
            />
            <StatCard
              title='Workspaces'
              value={formatNumber(overview.total_workspaces)}
              description='User-owned workspaces'
            />
            <StatCard
              title='Projects'
              value={formatNumber(overview.total_projects)}
              description='Projects across all workspaces'
            />
            <StatCard
              title='Datasets'
              value={formatNumber(overview.total_datasets)}
              description='Uploaded datasets'
            />
            <StatCard
              title='Dashboards'
              value={formatNumber(overview.total_dashboards)}
              description='Generated dataset dashboards'
            />
            <StatCard
              title='Charts'
              value={formatNumber(overview.total_charts)}
              description='Saved charts across dashboards'
            />
            <StatCard
              title='Total data rows'
              value={formatNumber(overview.total_rows)}
              description='Combined rows across datasets'
            />
          </div>
        </section>

        {/* Storage usage */}
        <section className='mt-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:flex sm:items-center sm:justify-between'>
          <div>
            <h2 className='font-bold'>Dataset storage</h2>
            <p className='mt-1 text-sm text-slate-500'>
              Combined file sizes recorded for uploaded datasets.
            </p>
          </div>
          <p className='mt-3 text-2xl font-bold text-slate-900 sm:mt-0'>
            {formatBytes(overview.storage_bytes)}
          </p>
        </section>

        {/* User management */}
        <section className='mt-10'>
          <div className='mb-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between'>
            <div>
              <h2 className='text-xl font-bold'>User management</h2>
              <p className='mt-1 text-sm text-slate-500'>
                Search accounts, inspect usage, and manage access.
              </p>
            </div>

            <p className='text-sm text-slate-500'>
              {formatNumber(totalUsers)} matching users
            </p>
          </div>

          {/* Search and filters */}
          <div className='mb-4 flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:flex-row'>
            <input
              type='search'
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder='Search by name or email...'
              aria-label='Search users'
              className='min-w-0 flex-1 rounded-lg border border-slate-300 px-4 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100'
            />

            <select
              value={roleFilter}
              onChange={(event) => {
                setRoleFilter(event.target.value);
                setPage(0);
              }}
              aria-label='Filter by role'
              className='rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm outline-none focus:border-blue-500'
            >
              <option value=''>All roles</option>
              <option value='user'>Users</option>
              <option value='admin'>Admins</option>
            </select>
          </div>

          {/* Users table */}
          <div className='overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm'>
            {loading ? (
              <div className='px-6 py-16 text-center text-sm text-slate-500'>
                Loading admin data...
              </div>
            ) : users.length === 0 ? (
              <div className='px-6 py-16 text-center'>
                <p className='font-semibold text-slate-700'>No users found</p>
                <p className='mt-1 text-sm text-slate-500'>
                  Try another search term or role filter.
                </p>
              </div>
            ) : (
              <div className='overflow-x-auto'>
                <table className='w-full min-w-[1250px] text-left text-sm'>
                  <thead className='border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500'>
                    <tr>
                      <th className='px-5 py-4 font-semibold'>User</th>
                      <th className='px-4 py-4 font-semibold'>Role</th>
                      <th className='px-4 py-4 font-semibold'>Account</th>
                      <th className='px-4 py-4 font-semibold'>Email</th>
                      <th className='px-4 py-4 font-semibold'>Joined</th>
                      {resourceColumns.map((column) => (
                        <th
                          key={column.key}
                          className='px-4 py-4 text-center font-semibold'
                        >
                          {column.label}
                        </th>
                      ))}
                      <th className='px-5 py-4 font-semibold'>Actions</th>
                    </tr>
                  </thead>

                  <tbody className='divide-y divide-slate-100'>
                    {users.map((targetUser) => {
                      const isSelf = targetUser.id === currentUser?.id;
                      const busy = actionUserId === targetUser.id;

                      return (
                        <tr
                          key={targetUser.id}
                          className='transition hover:bg-slate-50'
                        >
                          <td className='px-5 py-4'>
                            <div className='font-semibold text-slate-900'>
                              {targetUser.name}
                              {isSelf && (
                                <span className='ml-2 text-xs font-normal text-slate-400'>
                                  You
                                </span>
                              )}
                            </div>
                            <div className='mt-1 text-xs text-slate-500'>
                              ID: {targetUser.id}
                            </div>
                            <div className='mt-1 text-xs text-slate-500'>
                              {targetUser.email}
                            </div>
                          </td>

                          <td className='px-4 py-4'>
                            <span
                              className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                                targetUser.role === 'admin'
                                  ? 'bg-violet-50 text-violet-700'
                                  : 'bg-slate-100 text-slate-700'
                              }`}
                            >
                              {targetUser.role}
                            </span>
                          </td>

                          <td className='px-4 py-4'>
                            <StatusBadge active={targetUser.is_active} />
                          </td>

                          <td className='px-4 py-4'>
                            <VerificationBadge
                              verified={targetUser.email_verified}
                            />
                          </td>

                          <td className='whitespace-nowrap px-4 py-4 text-slate-600'>
                            {formatDate(targetUser.created_at)}
                          </td>

                          {resourceColumns.map((column) => (
                            <td
                              key={column.key}
                              className='px-4 py-4 text-center tabular-nums text-slate-600'
                            >
                              {formatNumber(targetUser[column.key] ?? 0)}
                            </td>
                          ))}

                          <td className='px-5 py-4'>
                            <div className='flex min-w-[155px] flex-col items-start gap-2'>
                              <button
                                type='button'
                                disabled={busy || isSelf}
                                onClick={() => handleStatusChange(targetUser)}
                                className='text-xs font-semibold text-slate-700 hover:text-slate-900 disabled:cursor-not-allowed disabled:opacity-40'
                              >
                                {targetUser.is_active
                                  ? 'Deactivate'
                                  : 'Reactivate'}
                              </button>

                              <button
                                type='button'
                                disabled={busy || isSelf}
                                onClick={() => handleDelete(targetUser)}
                                className='text-xs font-semibold text-red-600 hover:text-red-800 disabled:cursor-not-allowed disabled:opacity-40'
                              >
                                {busy ? 'Processing...' : 'Delete user'}
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}

            {/* Pagination */}
            <div className='flex flex-col gap-3 border-t border-slate-200 px-5 py-4 sm:flex-row sm:items-center sm:justify-between'>
              <p className='text-sm text-slate-500'>
                {totalUsers === 0
                  ? 'Showing 0 users'
                  : `Showing ${page * PAGE_SIZE + 1}–${Math.min(
                      (page + 1) * PAGE_SIZE,
                      totalUsers,
                    )} of ${formatNumber(totalUsers)}`}
              </p>

              <div className='flex items-center gap-2'>
                <button
                  type='button'
                  disabled={page === 0 || loading}
                  onClick={() => setPage((previous) => previous - 1)}
                  className='rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40'
                >
                  Previous
                </button>

                <span className='px-2 text-sm text-slate-600'>
                  Page {Math.min(page + 1, totalPages)} of {totalPages}
                </span>

                <button
                  type='button'
                  disabled={page + 1 >= totalPages || loading}
                  onClick={() => setPage((previous) => previous + 1)}
                  className='rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40'
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Audit logs */}
        <section className='mt-10'>
          <div className='mb-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between'>
            <div>
              <h2 className='text-xl font-bold'>Audit logs</h2>
              <p className='mt-1 text-sm text-slate-500'>
                Recent administrative actions recorded by DataPulse.
              </p>
            </div>
            <span className='text-sm text-slate-500'>Latest 10 events</span>
          </div>

          <div className='overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm'>
            {loading ? (
              <div className='px-6 py-10 text-center text-sm text-slate-500'>
                Loading audit logs...
              </div>
            ) : auditLogs.length === 0 ? (
              <div className='px-6 py-10 text-center text-sm text-slate-500'>
                No audit events have been recorded yet.
              </div>
            ) : (
              <div className='overflow-x-auto'>
                <table className='w-full min-w-[900px] text-left text-sm'>
                  <thead className='border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500'>
                    <tr>
                      <th className='px-5 py-4 font-semibold'>Action</th>
                      <th className='px-4 py-4 font-semibold'>Admin ID</th>
                      <th className='px-4 py-4 font-semibold'>Target user</th>
                      <th className='px-4 py-4 font-semibold'>Details</th>
                      <th className='px-5 py-4 font-semibold'>Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className='divide-y divide-slate-100'>
                    {auditLogs.map((log) => (
                      <tr key={log.id} className='hover:bg-slate-50'>
                        <td className='px-5 py-4'>
                          <span className='inline-flex rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700'>
                            {(log.action || 'unknown').replaceAll('_', ' ')}
                          </span>
                        </td>
                        <td className='px-4 py-4 text-slate-600'>
                          {log.admin_id ?? '—'}
                        </td>
                        <td className='px-4 py-4 text-slate-600'>
                          {log.target_user_id ??
                            log.details?.deleted_user_id ??
                            '—'}
                        </td>
                        <td className='max-w-sm px-4 py-4 text-xs text-slate-500'>
                          {log.details
                            ? Object.entries(log.details)
                                .map(
                                  ([key, value]) =>
                                    `${key.replaceAll('_', ' ')}: ${String(value)}`,
                                )
                                .join(' · ')
                            : '—'}
                        </td>
                        <td className='whitespace-nowrap px-5 py-4 text-slate-600'>
                          {log.created_at
                            ? new Date(log.created_at).toLocaleString('en-IN')
                            : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>

        <p className='mt-6 text-xs text-slate-400'>
          Storage reflects dataset file sizes recorded by the application, not
          total database disk usage. Active status indicates account access, not
          recent activity.
        </p>
      </main>
    </div>
  );
}

export default AdminDashboard;
