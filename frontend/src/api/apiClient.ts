// Configuración de la URL base de la API. 
// Se prioriza la variable de entorno VITE_API_URL y se asegura de que termine en '/api'
const rawUrl = import.meta.env.VITE_API_URL || "";
const API_BASE_URL = rawUrl.endsWith('/') ? rawUrl.slice(0, -1) : rawUrl;
export const API_URL = API_BASE_URL.endsWith('/api') ? API_BASE_URL : `${API_BASE_URL}/api`;

/**
 * Genera el header de autorización basado en las credenciales del usuario guardadas en localStorage.
 * Utiliza Autenticación Básica (Basic Auth) codificando 'usu_cod:usu_dni' en Base64.
 */
export const getAuthHeader = () => {
    const user = localStorage.getItem("user");
    if (!user) return {};
    const { usu_cod, usu_dni } = JSON.parse(user);
    // Basic Auth: btoa("usuario:password")
    return {
        'Authorization': `Basic ${btoa(`${usu_cod}:${usu_dni}`)}`,
    };
};

/**
 * Cliente genérico para realizar peticiones fetch a la API.
 * Inyecta automáticamente los headers de autenticación en cada llamada.
 */
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
