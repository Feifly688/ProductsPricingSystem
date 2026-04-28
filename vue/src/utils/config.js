const trimTrailingSlash = (value = '') => value.replace(/\/$/, '');
const legacyBackendAssetPattern = /^https?:\/\/[^/]+\/(?:api\/)?(files\/download|images|results\/images)\//i;

export const API_BASE_URL = trimTrailingSlash(
    import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_BASE_URL || ''
);

export const apiUrl = (path = '') => {
    if (/^https?:\/\//i.test(path)) return path;
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    return `${API_BASE_URL}${normalizedPath}`;
};

export const assetUrl = (path = '') => {
    if (!path) return '';
    if (legacyBackendAssetPattern.test(path)) {
        const url = new URL(path);
        return apiUrl(url.pathname.replace(/^\/api(?=\/)/, ''));
    }
    if (/^(https?:)?\/\//i.test(path) || path.startsWith('data:') || path.startsWith('blob:')) {
        return path;
    }
    return apiUrl(path);
};
