import { z } from 'zod';

const Env = z.object({
    VITE_API_BASE_URL: z.string().url(),
});

export const env = Env.parse({
    VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
});
