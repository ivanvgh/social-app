import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch } from '@/store';
import { setSession } from '@/store/auth/auth.slice';
import { authApi } from '@/features/auth/api';

export default function LoginPage() {
    const d = useAppDispatch();
    const nav = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [errMsg, setErrMsg] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const submit = async (e: React.FormEvent) => {
        e.preventDefault();
        setErrMsg(null);
        setLoading(true);
        try {
            const data = await authApi.login({ email, password });
            d(setSession({ token: data.access_token, user: data.user ?? null }));
            nav('/');
        } catch (err: any) {
            const status = err?.response?.status;
            const detail = err?.response?.data?.detail;
            if (status === 401) setErrMsg('Invalid email or password');
            else setErrMsg(detail || 'Unexpected error. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className='p-6 max-w-sm mx-auto'>
            <h1 className='text-xl font-semibold mb-4'>Login</h1>
            <form onSubmit={submit} className='space-y-3'>
                <input
                    className='w-full border p-2 rounded'
                    placeholder='email'
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                <input
                    className='w-full border p-2 rounded'
                    placeholder='password'
                    type='password'
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                {errMsg && <p className='text-sm text-red-600'>{errMsg}</p>}
                <button
                    className='w-full border p-2 rounded font-medium disabled:opacity-50'
                    type='submit'
                    disabled={loading}
                >
                    {loading ? 'Signing in…' : 'Sign in'}
                </button>
            </form>
        </div>
    );
}
