const rawUrl = import.meta.env.VITE_API_URL || "";
const API_BASE_URL = rawUrl.endsWith('/') ? rawUrl.slice(0, -1) : rawUrl;
export const API_URL = API_BASE_URL.endsWith('/api') ? API_BASE_URL : `${API_BASE_URL}/api`;

export const getAuthHeader = () => {
    const user = localStorage.getItem("user");
    if (!user) return {};
    const { usu_cod, usu_dni } = JSON.parse(user);
    return {
        'Authorization': `Basic ${btoa(`${usu_cod}:${usu_dni}`)}`,
    };
};

export const apiClient = async (endpoint: string, options: RequestInit = {}) => {
    const headers = {
        ...options.headers,
        ...getAuthHeader(),
    };

    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers,
    });

    return response;
};

export default apiClient;
