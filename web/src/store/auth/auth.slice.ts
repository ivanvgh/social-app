import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

type User = {
    id: string;
    username: string
} | null;
type AuthState = {
    accessToken: string | null;
    user: User
};

const initialState: AuthState = {
    accessToken: null,
    user: null
};

const slice = createSlice({
        name: 'auth',
        initialState,
        reducers: {
            setSession: (state, action: PayloadAction<{ token: string; user: User }>) => {
                state.accessToken = action.payload.token;
                state.user = action.payload.user;
            },
            updateToken: (state, action: PayloadAction<string | null>) => {
                state.accessToken = action.payload;
            },
            clearSession: (state) => {
                state.accessToken = null;
                state.user = null;
            },
        },
    });

export const {
    setSession,
    updateToken,
    clearSession
} = slice.actions;
export default slice.reducer;
