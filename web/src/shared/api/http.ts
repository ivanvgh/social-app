import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios';
import { env } from '@/shared/config/env';
import { getCsrfToken } from '@/shared/lib/csrf';

let accessToken: string | null = null;
let onTokenRefreshed: ((t: string | null) => void) | null = null;
let refreshing: Promise<string> | null = null;

export const setAccessToken = (t: string | null) => {
    accessToken = t;
    onTokenRefreshed?.(t);
};

export const setAccessTokenListener = (cb: (t: string | null) => void) => {
    onTokenRefreshed = cb;
};

const attachAuth = (cfg: InternalAxiosRequestConfig) => {
    if (accessToken) cfg.headers.Authorization = `Bearer ${accessToken}`;
    return cfg;
};

const refreshOnce = async (http: AxiosInstance) => {
    const csrf = getCsrfToken();
    const { data } = await http.post('/auth/refresh', {}, {
        headers: { 'x-csrf-token': csrf },
        withCredentials: true,
    });
    return data.access_token as string;
};

// NEW: treat any URL containing `/auth/` as non-refreshable
const isAuthPath = (url?: string) => !!url && /\/auth\//.test(url);

export const makeHttp = (baseURL = env.VITE_API_BASE_URL) => {
    const http = axios.create({ baseURL, withCredentials: true });

    http.interceptors.request.use((cfg) => attachAuth(cfg));

    http.interceptors.response.use(
        (r) => r,
        async (err) => {
            const cfg = (err?.config ?? {}) as InternalAxiosRequestConfig & { __retry?: boolean };
            const status = err?.response?.status;

            // If it's not 401, we've already retried, or it's an auth route → just bubble up
            if (status !== 401 || cfg.__retry || isAuthPath(cfg.url)) throw err;

            // Single-flight refresh for regular API requests
            cfg.__retry = true;
            refreshing = refreshing ?? refreshOnce(http);
            try {
                const token = await refreshing;
                refreshing = null;
                setAccessToken(token);
                return http(cfg);
            } catch (e) {
                refreshing = null;
                setAccessToken(null);
                throw e;
            }
        },
    );

    return http;
};
