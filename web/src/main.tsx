import { StrictMode } from 'react';
import ReactDOM from 'react-dom/client';
import '@/app/styles/tailwind.css';
import { Provider } from 'react-redux';
import { store } from '@/store';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider, createBrowserRouter } from 'react-router-dom';
import { ProtectedRoute } from '@/router/ProtectedRoute';
import { PublicOnlyRoute } from '@/router/PublicOnlyRoute';
import HomePage from '@/pages/home/HomePage';
import LoginPage from '@/pages/login/LoginPage';
import RegisterPage from '@/pages/register/RegisterPage';
import ProfilePage from '@/pages/profile/ProfilePage';
import NotFoundPage from '@/pages/not-found/NotFoundPage';

const qc = new QueryClient();

const router = createBrowserRouter([
    { path: '/login', element: <PublicOnlyRoute><LoginPage /></PublicOnlyRoute> },
    { path: '/register', element: <PublicOnlyRoute><RegisterPage /></PublicOnlyRoute> },
    { path: '/', element: <ProtectedRoute><HomePage /></ProtectedRoute> },
    { path: '/profile', element: <ProtectedRoute><ProfilePage /></ProtectedRoute> },
    { path: '*', element: <NotFoundPage /> },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <Provider store={store}>
            <QueryClientProvider client={qc}>
                <RouterProvider router={router} />
            </QueryClientProvider>
        </Provider>
    </StrictMode>,
);
