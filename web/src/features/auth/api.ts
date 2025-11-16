import { makeHttp, setAccessToken } from '@/shared/api/http';

const http = makeHttp();

export const authApi = {
    login: async (payload: { email: string; password: string }) => {
        const { data } = await http.post('/v1/auth/login', payload);
        setAccessToken(data.access_token);
        return data; // { access_token, user }
    },
    register: async (payload: { email: string; username: string; password: string }) => {
        const { data } = await http.post('/v1/auth/register', payload);
        setAccessToken(data.access_token);
        return data;
    },
    logout: async () => {
        await http.post('/v1/auth/logout');
        setAccessToken(null);
    },
    logoutAll: async () => {
        await http.post('/v1/auth/logout-all');
        setAccessToken(null);
    },
};
