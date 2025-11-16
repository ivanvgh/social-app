import 'axios';

declare module 'axios' {
    // internal flag so we don't retry twice
    export interface InternalAxiosRequestConfig {
        __retry?: boolean;
    }
}
