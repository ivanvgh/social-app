import type { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAppSelector } from '@/store';

type Props = { children: ReactNode };

export function PublicOnlyRoute({ children }: Props) {
    const token = useAppSelector((state) => state.auth.accessToken);
    if (token) return <Navigate to="/" replace />;
    return children;
}
