const KEY = 'csrf_token';

const gen = (): string => {
    const arr = new Uint8Array(16);
    crypto.getRandomValues(arr);
    return Array.from(arr).map(
        (b) => b.toString(16)
            .padStart(2, '0')
    ).join('');
};

export const getCsrfToken = (): string => {
    const fromStorage = localStorage.getItem(KEY);
    if (fromStorage) return fromStorage;
    const t: string = gen();
    localStorage.setItem(KEY, t);
    document.cookie = `${KEY}=${t}; SameSite=Strict; Path=/`;
    return t;
};
