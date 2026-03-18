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

export const userService = {
    login: async (username: string, dni: string) => {
        const response = await fetch(`${API_URL}/users/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, dni }),
        });
        return response;
    },

    getUserScore: async (usu_cod: string) => {
        return apiClient(`/users/score/${usu_cod}/`);
    },

    listUsers: async () => {
        return apiClient(`/users/list/`);
    },

    importUsers: async (file: File) => {
        const form = new FormData();
        form.append('file', file);
        return fetch(`${API_URL}/users/import/`, {
            method: 'POST',
            headers: { ...getAuthHeader() },
            body: form,
        });
    },

    cleanupInactive: async (months: number, deleteUsers: boolean) => {
        return apiClient(`/users/cleanup/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ months, delete: deleteUsers }),
        });
    },

    getRanking: async () => {
        return apiClient(`/users/ranking/`);
    },

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
