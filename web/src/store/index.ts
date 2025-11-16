import { configureStore } from '@reduxjs/toolkit';
import { type TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import auth, { updateToken } from './auth/auth.slice';
import { setAccessTokenListener } from '@/shared/api/http';

export const store = configureStore({ reducer: { auth } });

setAccessTokenListener((token: string | null) => { store.dispatch(updateToken(token)); });

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
