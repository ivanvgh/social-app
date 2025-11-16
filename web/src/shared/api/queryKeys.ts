export const qk = {
    me: ['me'] as const,
    feed: (page: number) => ['posts', 'feed', page] as const,
    comments: (postId: string, page: number) => ['comments', postId, page] as const,
};
