import { apiClient, getAuthHeader, API_URL } from "./apiClient";

export interface Rank {
    id: number;
    name: string;
    description: string;
    badge_image: string | null;
}

export interface User {
    usu_cod: string;
    username: string;
    usu_dni: string;
    usu_nom: string;
    usu_sex: 'M' | 'F' | null;
    usu_edad: number;
    usu_pun_tot: number;
    cat_cod: string | null;
    ran_sig: number | null;
    usu_fec_ult: string | null;
    usu_reg: string;
    is_staff: boolean;
    usu_fot?: string | null;
    ran_nom?: string;
}

export interface ImportResult {
    creados: number;
    actualizados: number;
    total_procesados: number;
    errores: { fila: number; motivo: string }[];
}

export interface CleanupResult {
    accion: string;
    cantidad: number;
    mensaje: string;
}

/**
 * Servicio para gestionar las operaciones relacionadas con los usuarios.
 */
export const userService = {
    /**
     * Realiza el login del usuario enviando username y dni.
     * No utiliza apiClient porque aún no tenemos las credenciales para el Basic Auth.
     */
    login: async (username: string, dni: string) => {
        const response = await fetch(`${API_URL}/users/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, dni }),
        });
        return response;
    },

    /**
     * Obtiene los datos detallados y puntaje de un usuario específico.
     */
    getUserScore: async (usu_cod: string) => {
        return apiClient(`/users/score/${usu_cod}/`);
    },

    /**
     * Lista todos los usuarios (requiere permisos de Admin/Staff).
     */
    listUsers: async () => {
        return apiClient(`/users/list/`);
    },

    /**
     * Sube un archivo Excel para importar o actualizar usuarios de forma masiva.
     */
    importUsers: async (file: File) => {
        const form = new FormData();
        form.append('file', file);
        return fetch(`${API_URL}/users/import/`, {
            method: 'POST',
            headers: { ...getAuthHeader() },
            body: form,
        });
    },

    /**
     * Limpia o resetea puntos de usuarios inactivos basándose en meses de inactividad.
     */
    cleanupInactive: async (months: number, deleteUsers: boolean) => {
        return apiClient(`/users/cleanup/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ months, delete: deleteUsers }),
        });
    },

    /**
     * Obtiene el ranking global de usuarios y la posición del usuario actual.
     */
    getRanking: async () => {
        return apiClient(`/users/ranking/`);
    },

    /**
     * Descarga la plantilla de Excel oficial para la importación de usuarios.
     */
    downloadTemplate: async () => {
        const res = await fetch(`${API_URL}/users/template/`, {
            headers: { ...getAuthHeader() },
        });
        if (!res.ok) throw new Error("Error al descargar la plantilla");
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'plantilla_usuarios.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    },
};
