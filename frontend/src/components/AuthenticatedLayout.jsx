import { Outlet } from 'react-router-dom';

import Sidebar from './SideBar';

function AuthenticatedLayout() {
  return (
    <div className='min-h-screen bg-stone-50'>
      <Sidebar />

      <main className='min-h-screen lg:pl-64'>
        <Outlet />
      </main>
    </div>
  );
}

export default AuthenticatedLayout;
