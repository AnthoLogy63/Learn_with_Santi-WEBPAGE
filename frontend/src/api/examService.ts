import { apiClient, getAuthHeader, API_URL } from "./apiClient";

export interface Exam {
    exa_cod: string;
    exa_nom: string;
    exa_des: string;
    exa_fot?: string | null;
    status?: string;
}

export interface Categoria {
    cat_cod: string;
    cat_nom: string;
}

export interface Competencia {
    com_cod: string;
    com_nom: string;
    com_des: string | null;
}

export interface TipoPregunta {
    tip_pre_cod: number;
    tip_pre_nom: string;
}

export interface ExamOption {
    opc_cod: string;
    opc_tex: string;
    opc_cor: boolean;
}

export interface LocalOption extends ExamOption {
    isNew?: boolean;
    isDirty?: boolean;
    isDeleted?: boolean;
}

export interface Question {
    pre_cod: string;
    pre_tex: string;
    pre_fot: string | null;
    pre_pun: number;
    pre_tie: number;
    tip_pre_cod?: number;
    com_cod?: string;
    options: LocalOption[];
}

export interface LocalQuestion extends Question {
    isNew?: boolean;
    isDirty?: boolean;
    isDeleted?: boolean;
    tempImageFile?: File;
    tempImageUrl?: string;
}

export interface ExamImportResult {
    modo: "creado" | "reemplazado";
    exam_id: number;
    exam_name: string;
    preguntas_creadas: number;
    opciones_creadas: number;
    errores: string[];
}

export const examService = {
    getExams: async (): Promise<Exam[]> => {
        const res = await apiClient("/exams/");
        return res.json();
    },

    getCategorias: async (): Promise<Categoria[]> => {
        const res = await apiClient("/exams/categorias/");
        return res.json();
    },

    getCompetencias: async (): Promise<Competencia[]> => {
        const res = await apiClient("/exams/competencias/");
        return res.json();
    },

    getTipoPreguntas: async (): Promise<TipoPregunta[]> => {
        const res = await apiClient("/exams/tipos-pregunta/");
        return res.json();
    },

    createExam: async (data: Partial<Exam>) => {
        return apiClient("/exams/", {
            method: 'POST',
            body: JSON.stringify(data),
            headers: { 'Content-Type': 'application/json' },
        });
    },

    assignCategoryToExam: async (exa_cod: string, cat_cod: string) => {
        return apiClient("/exams/categoria_examen/", {
            method: 'POST',
            body: JSON.stringify({ exa_cod, cat_cod }),
            headers: { 'Content-Type': 'application/json' },
        });
    },

    assignCompetenceToExam: async (data: { exa_cod: string, cat_cod: string, com_cod: string, num_preguntas: number }) => {
        return apiClient("/exams/examen_categoria_competencia/", {
            method: 'POST',
            body: JSON.stringify(data),
            headers: { 'Content-Type': 'application/json' },
        });
    },

    startOrResume: async (exa_cod: string) => {
        return apiClient(`/exams/${exa_cod}/start_or_resume/`, {
            method: 'GET'
        });
    },

    saveProgress: async (exa_cod: string, int_cod: string, respuestas: any[]) => {
        return apiClient(`/exams/${exa_cod}/save_progress/`, {
            method: 'POST',
            body: JSON.stringify({ int_cod, respuestas }),
            headers: { 'Content-Type': 'application/json' },
        });
    },

    finishAttempt: async (exa_cod: string, int_cod: string) => {
        return apiClient(`/exams/${exa_cod}/finish_attempt/`, {
            method: 'POST',
            body: JSON.stringify({ int_cod }),
            headers: { 'Content-Type': 'application/json' },
        });
    },

    updateExam: async (exa_cod: string, data: Partial<Exam>) => {
        return apiClient(`/exams/${exa_cod}/`, {
            method: 'PATCH',
            body: JSON.stringify(data),
            headers: { 'Content-Type': 'application/json' },
        });
    },

    deleteExam: async (exa_cod: string) => {
        return apiClient(`/exams/${exa_cod}/`, {
            method: 'DELETE',
        });
    },

    // CRUD Questions
    getAllQuestions: async (exa_cod: string): Promise<Question[]> => {
        const res = await apiClient(`/exams/questions/?exa_cod=${exa_cod}`);
        return res.json();
    },

    // CRUD Questions
    createQuestion: async (exa_cod: string, formData: FormData) => {
        return fetch(`${API_URL}/exams/questions/?exa_cod=${exa_cod}`, {
            method: 'POST',
            headers: { ...getAuthHeader() },
            body: formData,
        });
    },

    updateQuestion: async (pre_cod: string, formData: FormData) => {
        return fetch(`${API_URL}/exams/questions/${pre_cod}/`, {
            method: 'PATCH',
            headers: { ...getAuthHeader() },
            body: formData,
        });
    },

    deleteQuestion: async (pre_cod: string) => {
        return apiClient(`/exams/questions/${pre_cod}/`, {
            method: 'DELETE',
        });
    },

    // CRUD Options
    createOption: async (pre_cod: string, data: Partial<ExamOption>) => {
        return apiClient(`/exams/options/`, {
            method: 'POST',
            body: JSON.stringify({ ...data, pre_cod }),
            headers: { 'Content-Type': 'application/json' },
        });
    },

    updateOption: async (opc_cod: string, data: Partial<ExamOption>) => {
        return apiClient(`/exams/options/${opc_cod}/`, {
            method: 'PATCH',
            body: JSON.stringify(data),
            headers: { 'Content-Type': 'application/json' },
        });
    },

    deleteOption: async (opc_cod: string) => {
        return apiClient(`/exams/options/${opc_cod}/`, {
            method: 'DELETE',
        });
    },

    getUserResults: async (search: string = "", offset: number = 0) => {
        return apiClient(`/exams/attempts/user_results/?search=${search}&offset=${offset}`);
    },

    importExam: async (file: File) => {
        const form = new FormData();
        form.append('file', file);
        return fetch(`${API_URL}/exams/import/`, {
            method: 'POST',
            headers: { ...getAuthHeader() },
            body: form,
        });
    },

    getExamConfig: async (exa_cod: string) => {
        const res = await apiClient(`/exams/${exa_cod}/get_config/`);
        return res.json();
    },

    bulkUpdateExam: async (exa_cod: string, data: any) => {
        return apiClient(`/exams/${exa_cod}/bulk_save/`, {
            method: 'POST',
            body: JSON.stringify(data),
            headers: { 'Content-Type': 'application/json' },
        });
    },

    getStatsSummary: async () => {
        return apiClient(`/exams/stats_summary/`);
    },

    exportResults: async (exa_cod: string | number) => {
        const res = await fetch(`${API_URL}/exams/${exa_cod}/export_results/`, {
            headers: { ...getAuthHeader() },
        });
        return res;
    },

    downloadTemplate: async () => {
        const res = await fetch(`${API_URL}/exams/template/`, {
            headers: { ...getAuthHeader() },
        });
        if (!res.ok) throw new Error("Error al descargar la plantilla");
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'plantilla_examen.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    },
};


