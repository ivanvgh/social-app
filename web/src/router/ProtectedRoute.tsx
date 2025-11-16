import { type ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAppSelector } from '@/store';

type Props = { children: ReactNode };

export function ProtectedRoute({ children }: Props) {
    const token = useAppSelector((s) => s.auth.accessToken);
    const loc = useLocation();
    if (!token) return <Navigate to="/login" replace state={{ next: loc.pathname }} />;
    return children;
}
