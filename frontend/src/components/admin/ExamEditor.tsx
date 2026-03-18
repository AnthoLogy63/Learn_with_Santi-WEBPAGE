import { useState, useEffect } from "react";
import { X, Save, Eye, Plus, Loader2, HelpCircle } from "lucide-react";
import { examService, Exam, LocalQuestion, LocalOption, TipoPregunta } from "@/api/examService";
import { toast } from "sonner";
import AdminExamPreview from "./AdminExamPreview";
import ExamConfig, { CategoryConfig } from "./ExamConfig";
import QuestionCard from "./QuestionCard";

interface ExamEditorProps {
    exa_cod: string;
    onClose: () => void;
    onSaveSuccess?: () => void;
}

const ExamEditor = ({ exa_cod, onClose, onSaveSuccess }: ExamEditorProps) => {
    const [exam, setExam] = useState<Exam | null>(null);
    const [questions, setQuestions] = useState<LocalQuestion[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [expandedQuestion, setExpandedQuestion] = useState<string | null>(null);
    const [showPreview, setShowPreview] = useState(false);
    const [hasChanges, setHasChanges] = useState(false);
    const [config, setConfig] = useState<CategoryConfig[]>([]);
    const [allCompetencies, setAllCompetencies] = useState<Competencia[]>([]);
    const [tipoPreguntas, setTipoPreguntas] = useState<TipoPregunta[]>([]);

    useEffect(() => {
        fetchExamData();
    }, [exa_cod]);

    useEffect(() => {
        const changed = questions.some(q => q.isDirty || q.isNew || q.isDeleted || q.options.some(o => o.isDirty || o.isNew || o.isDeleted));
        setHasChanges(changed);

        const handleBeforeUnload = (e: BeforeUnloadEvent) => {
            if (changed) {
                e.preventDefault();
                e.returnValue = "";
            }
        };
        window.addEventListener("beforeunload", handleBeforeUnload);
        return () => window.removeEventListener("beforeunload", handleBeforeUnload);
    }, [questions]);

    const fetchExamData = async () => {
        setLoading(true);
        try {
            const [examsRes, tiposRes, compsRes] = await Promise.all([
                examService.getExams(),
                examService.getTipoPreguntas(),
                examService.getCompetencias()
            ]);
            setTipoPreguntas(tiposRes);
            setAllCompetencies(compsRes);
            
            const currentExam = examsRes.find((e: Exam) => e.exa_cod === exa_cod);
            setExam(currentExam || null);

            if (currentExam) {
                const questionsRes = await examService.getAllQuestions(currentExam.exa_cod);
                // La API de DRF devuelve un array directamente, no un objeto {questions: []}
                const questionsData = Array.isArray(questionsRes) ? questionsRes : ((questionsRes as any).questions || []);
                
                setQuestions(questionsData.map((q: any) => ({
                    ...q,
                    options: (q.options || q.opciones || []).map((o: any) => ({ ...o }))
                })));
            }
        } catch (error) {
            console.error("Error fetching exam data:", error);
            toast.error("Error al cargar los datos del examen");
        } finally {
            setLoading(false);
        }
    };


    const handleSaveEverything = async () => {
        if (!exam) return;
        setSaving(true);
        try {
            // Recolectamos toda la información para enviarla de una sola vez
            // No filtramos localmente para asegurar sincronización completa como pidió el usuario
            const payload = {
                exa_nom: exam.exa_nom,
                exa_des: exam.exa_des,
                questions: questions.map(q => ({
                    pre_cod: q.pre_cod,
                    pre_tex: q.pre_tex,
                    pre_pun: q.pre_pun,
                    pre_tie: q.pre_tie,
                    pre_fot: q.pre_fot,
                    tip_pre_cod: q.tip_pre_cod || 1,
                    com_cod: q.com_cod,
                    isNew: q.isNew,
                    isDirty: q.isDirty,
                    isDeleted: q.isDeleted,
                    options: q.options.map(o => ({
                        opc_cod: o.opc_cod,
                        opc_tex: o.opc_tex,
                        opc_cor: o.opc_cor,
                        isNew: o.isNew,
                        isDirty: o.isDirty,
                        isDeleted: o.isDeleted,
                    }))
                })),
                config: config
            };

            // VALIDACIÓN: Verificar si hay suficientes preguntas por competencia
            const activeQuestions = questions.filter(q => !q.isDeleted);
            const countsPerComp: Record<string, number> = {};
            activeQuestions.forEach(q => {
                if (q.com_cod) {
                    countsPerComp[q.com_cod] = (countsPerComp[q.com_cod] || 0) + 1;
                }
            });

            const validationErrors: string[] = [];
            config.forEach(cc => {
                cc.competencies.forEach(comp => {
                    const available = countsPerComp[comp.com_cod] || 0;
                    if (available < comp.num_preguntas) {
                        const compName = allCompetencies.find(c => c.com_cod === comp.com_cod)?.com_nom || comp.com_cod;
                        validationErrors.push(`Faltan preguntas para "${compName}": se requieren ${comp.num_preguntas} y hay ${available}.`);
                    }
                });
            });

            if (validationErrors.length > 0) {
                validationErrors.forEach(err => toast.error(err, { duration: 5000 }));
                if (!confirm("Atención: Hay discrepancias en la cantidad de preguntas requeridas por competencia. ¿Deseas guardar de todos modos?")) {
                    setSaving(false);
                    return;
                }
            }

            const res = await examService.bulkUpdateExam(exam.exa_cod, payload);
            if (!res.ok) throw new Error("Error en el guardado masivo");

            const updateData = await res.json();
            
            // 2. Procesar imágenes pendientes (solo si hay archivos temporales)
            // Creamos un mapa de las preguntas actualizadas del servidor para facilitar la búsqueda
            // El servidor devuelve el estado completo de las preguntas del examen
            const serverQuestions = updateData.questions || [];
            
            const questionsWithImages = questions.filter(q => q.tempImageFile && !q.isDeleted);
            const imageUpdateMap: Record<string, string> = {};

            if (questionsWithImages.length > 0) {
                toast.loading("Subiendo imágenes...", { id: "img-upload" });
                for (const localQ of questionsWithImages) {
                    // Buscar la pregunta en la respuesta del servidor (por texto o código original)
                    const serverQ = serverQuestions.find((sq: any) => 
                        sq.pre_tex === localQ.pre_tex && 
                        (localQ.isNew ? true : sq.pre_cod === localQ.pre_cod)
                    );

                    if (serverQ && localQ.tempImageFile) {
                        const formData = new FormData();
                        formData.append('pre_fot', localQ.tempImageFile);
                        const imgRes = await examService.updateQuestion(serverQ.pre_cod, formData);
                        if (imgRes.ok) {
                            const updatedQ = await imgRes.json();
                            imageUpdateMap[serverQ.pre_cod] = updatedQ.pre_fot;
                        }
                    }
                }
                toast.dismiss("img-upload");
            }

            // 3. Sincronización Silenciosa del Estado
            // En lugar de recargar todo, mapeamos los IDs del servidor al estado local
            setQuestions(prev => {
                // Filtramos las borradas antes de sincronizar
                const remaining = prev.filter(q => !q.isDeleted);
                
                return remaining.map((localQ, idx) => {
                    // Buscamos la data fresca del servidor para esta posición/pregunta
                    const serverQ = serverQuestions.find((sq: any) => 
                        sq.pre_tex === localQ.pre_tex && 
                        (localQ.isNew ? true : sq.pre_cod === localQ.pre_cod)
                    );

                    if (!serverQ) return localQ;

                    // Si subimos imagen, usamos la ruta que devolvió el upload individual
                    const freshPreFot = imageUpdateMap[serverQ.pre_cod] || serverQ.pre_fot;

                    return {
                        ...serverQ,
                        pre_fot: freshPreFot,
                        // Limpiamos estados temporales
                        isNew: false,
                        isDirty: false,
                        isDeleted: false,
                        tempImageFile: undefined,
                        tempImageUrl: undefined,
                        // Sincronizar opciones (especialmente IDs de nuevas opciones)
                        options: (serverQ.options || serverQ.opciones || []).map((so: any) => ({
                            ...so,
                            isNew: false,
                            isDirty: false,
                            isDeleted: false
                        }))
                    };
                });
            });

            toast.success("Todo guardado correctamente");
            setHasChanges(false);
            onSaveSuccess?.();
        } catch (error) {
            console.error("Bulk save error:", error);
            toast.error("Ocurrió un error al guardar los cambios masivos");
        } finally {
            setSaving(false);
        }
    };

    const handleAddQuestion = () => {
        // Try to find Multiple Choice type (usually cod 1)
        const defaultType = tipoPreguntas.find(tp => tp.tip_pre_nom.toLowerCase().includes('múltiple') || tp.tip_pre_nom.toLowerCase().includes('multiple'))?.tip_pre_cod 
                           || (tipoPreguntas.length > 0 ? tipoPreguntas[0].tip_pre_cod : 1);

        const newQ: LocalQuestion = {
            pre_cod: `NEW_${Math.random()}`,
            pre_tex: "Nueva Pregunta",
            pre_fot: null,
            pre_pun: 10,
            pre_tie: 60,
            tip_pre_cod: defaultType,
            options: [],
            isNew: true
        };

        // If it happens to start as T/F (cod 4), init options
        if (defaultType === 4) {
            newQ.options = [
                { opc_cod: `OPT_TF_V_${Math.random()}`, opc_tex: 'Verdadero', opc_cor: true, isNew: true },
                { opc_cod: `OPT_TF_F_${Math.random()}`, opc_tex: 'Falso', opc_cor: false, isNew: true }
            ];
        }

        setQuestions([...questions, newQ]);
        setExpandedQuestion(newQ.pre_cod);
    };

    const handleDeleteQuestion = (pre_cod: string) => {
        setQuestions(questions.map(q => q.pre_cod === pre_cod ? { ...q, isDeleted: true } : q));
    };

    const handleUpdateQuestion = (pre_cod: string, data: Partial<LocalQuestion>, file?: File) => {
        setQuestions(questions.map(q => {
            if (q.pre_cod === pre_cod) {
                let updated = { ...q, ...data, isDirty: true };

                // Smart Type Switching Logic
                if (data.tip_pre_cod !== undefined && data.tip_pre_cod !== q.tip_pre_cod) {
                    const oldType = q.tip_pre_cod;
                    const newType = data.tip_pre_cod;

                    // If moving TO or FROM T/F (4), we should probably reset options to avoid mess
                    if (newType === 4 || oldType === 4) {
                        if (newType === 4) {
                            updated.options = [
                                { opc_cod: `OPT_TF_V_${Math.random()}`, opc_tex: 'Verdadero', opc_cor: true, isNew: true },
                                { opc_cod: `OPT_TF_F_${Math.random()}`, opc_tex: 'Falso', opc_cor: false, isNew: true }
                            ];
                        } else {
                            // If moving away from T/F, just clear options
                            updated.options = [];
                        }
                    } 
                    // If moving TO Relationship (3), mark all as correct
                    else if (newType === 3) {
                        updated.options = updated.options.map(o => ({ ...o, opc_cor: true }));
                    }
                }

                if (file) {
                    updated.tempImageFile = file;
                    updated.tempImageUrl = URL.createObjectURL(file);
                }
                return updated;
            }
            return q;
        }));
    };

    const handleAddOption = (pre_cod: string) => {
        setQuestions(questions.map(q => {
            if (q.pre_cod === pre_cod) {
                const newOpt: LocalOption = {
                    opc_cod: `OPT_NEW_${Math.random()}`,
                    opc_tex: q.tip_pre_cod === 3 ? 'A | B' : 'Nueva opción',
                    opc_cor: q.tip_pre_cod === 3 ? true : false,
                    isNew: true
                };
                return { ...q, options: [...q.options, newOpt] };
            }
            return q;
        }));
    };

    const handleUpdateOption = (pre_cod: string, opc_cod: string, data: Partial<LocalOption>) => {
        setQuestions(questions.map(q => {
            if (q.pre_cod === pre_cod) {
                return {
                    ...q,
                    options: q.options.map(o => o.opc_cod === opc_cod ? { ...o, ...data, isDirty: true } : o)
                };
            }
            return q;
        }));
    };

    const handleDeleteOption = (pre_cod: string, opc_cod: string) => {
        setQuestions(questions.map(q => {
            if (q.pre_cod === pre_cod) {
                return {
                    ...q,
                    options: q.options.map(o => o.opc_cod === opc_cod ? { ...o, isDeleted: true } : o)
                };
            }
            return q;
        }));
    };

    const handleClose = () => {
        if (hasChanges) {
            if (confirm("Tienes cambios sin guardar. ¿Estás seguro de que quieres salir?")) {
                onClose();
            }
        } else {
            onClose();
        }
    };

    if (loading) {
        return (
            <div className="fixed inset-0 bg-[#001c4d]/80 backdrop-blur-xl z-[60] flex items-center justify-center">
                <Loader2 className="h-10 w-10 animate-spin text-white" />
            </div>
        );
    }

    return (
        <div className="fixed inset-0 bg-[#001c4d] z-[60] overflow-y-auto animate-fade-in flex flex-col">
            {/* Header Sticky */}
            <div className="sticky top-0 bg-[#001c4d]/90 backdrop-blur-md border-b border-white/10 p-4 md:p-6 z-10 flex justify-between items-center shadow-lg">
                <div className="flex items-center gap-4">
                    <button onClick={handleClose} className="p-2 hover:bg-white/10 rounded-full transition-colors text-white">
                        <X size={24} />
                    </button>
                    <div>
                        <h2 className="text-xl md:text-2xl font-black text-white tracking-tight">Editor de Evaluación</h2>
                        <p className="text-white/40 text-[10px] uppercase font-black tracking-widest">CÓDIGO: {exa_cod} {hasChanges && <span className="text-amber-400 ml-2">(Cambios sin guardar)</span>}</p>
                    </div>
                </div>
                <div className="flex gap-4">
                    <button
                        onClick={() => setShowPreview(true)}
                        className="flex items-center gap-2 bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 px-6 py-2.5 rounded-xl font-black uppercase tracking-widest text-xs hover:bg-indigo-500/30 transition-all shadow-lg"
                    >
                        <Eye size={18} />
                        Vista Previa
                    </button>
                    <button
                        onClick={handleSaveEverything}
                        disabled={saving || !hasChanges}
                        className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-2.5 rounded-xl font-black uppercase tracking-widest text-xs shadow-xl transition-all disabled:opacity-50"
                    >
                        {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save size={18} />}
                        Guardar Cambios
                    </button>
                </div>
            </div>

            {/* Modal de Vista Previa */}
            {showPreview && exam && (
                <AdminExamPreview
                    exa_cod={exa_cod}
                    exa_nom={exam.exa_nom}
                    onClose={() => setShowPreview(false)}
                />
            )}

            <div className="max-w-5xl mx-auto w-full p-4 md:p-8 space-y-8 flex-1">

                {/* Exam Settings Card */}
                <section className="bg-white/5 border border-white/10 rounded-3xl p-6 md:p-8 space-y-6">
                    <div className="space-y-2">
                        <label className="text-[10px] font-black text-white/40 uppercase tracking-widest ml-1">Nombre del Examen</label>
                        <input
                            type="text"
                            value={exam?.exa_nom || ""}
                            onChange={(e) => setExam(exam ? { ...exam, exa_nom: e.target.value } : null)}
                            className="w-full bg-white/5 border border-white/20 rounded-2xl py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-white/20 font-bold"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-[10px] font-black text-white/40 uppercase tracking-widest ml-1">Descripción</label>
                        <textarea
                            rows={3}
                            value={exam?.exa_des || ""}
                            onChange={(e) => setExam(exam ? { ...exam, exa_des: e.target.value } : null)}
                            className="w-full bg-white/5 border border-white/20 rounded-2xl py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-white/20 font-medium"
                        />
                    </div>
                </section>

                {/* NEW CONFIG SECTION */}
                <ExamConfig 
                    exa_cod={exa_cod} 
                    allCompetencies={allCompetencies}
                    onConfigChange={(newConfig) => {
                        setConfig(newConfig);
                        setHasChanges(true);
                    }} 
                />

                {/* Questions Section */}
                <div className="space-y-6">
                    <div className="flex justify-between items-center px-2">
                        <h3 className="text-lg md:text-xl font-black text-white uppercase tracking-[0.2em]">Talonario de Preguntas</h3>
                        <button
                            onClick={handleAddQuestion}
                            className="flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-xl border border-white/20 transition-all text-[10px] font-black uppercase tracking-widest"
                        >
                            <Plus size={16} />
                            Añadir Pregunta
                        </button>
                    </div>

                    <div className="space-y-4 pb-20">
                        {questions.filter(q => !q.isDeleted).map((q, idx) => (
                            <QuestionCard
                                key={q.pre_cod}
                                question={q}
                                index={idx}
                                isExpanded={expandedQuestion === q.pre_cod}
                                tipoPreguntas={tipoPreguntas}
                                allCompetencies={allCompetencies}
                                onToggleExpand={() => setExpandedQuestion(expandedQuestion === q.pre_cod ? null : q.pre_cod)}
                                onDeleteQuestion={() => handleDeleteQuestion(q.pre_cod)}
                                onUpdateQuestion={(data, file) => handleUpdateQuestion(q.pre_cod, data, file)}
                                onUpdateOption={(opc_cod, data) => handleUpdateOption(q.pre_cod, opc_cod, data)}
                                onDeleteOption={(opc_cod) => handleDeleteOption(q.pre_cod, opc_cod)}
                                onToggleCorrect={(opc_cod) => {
                                    // For T/F, ensure only one is correct
                                    if (q.tip_pre_cod === 4) {
                                        setQuestions(questions.map(qus => qus.pre_cod === q.pre_cod ? {
                                            ...qus,
                                            options: qus.options.map(o => ({ ...o, opc_cor: o.opc_cod === opc_cod }))
                                        } : qus));
                                    } else {
                                        handleUpdateOption(q.pre_cod, opc_cod, { opc_cor: !q.options.find(o => o.opc_cod === opc_cod)?.opc_cor });
                                    }
                                }}
                                onAddOption={() => handleAddOption(q.pre_cod)}
                            />
                        ))}
                        {questions.filter(q => !q.isDeleted).length === 0 && (
                            <div className="py-20 text-center bg-white/5 rounded-[40px] border-2 border-dashed border-white/10">
                                <HelpCircle className="h-12 w-12 text-white/20 mx-auto mb-4" />
                                <p className="text-white/60 font-black uppercase tracking-[0.2em] text-sm">No hay preguntas añadidas</p>
                                <p className="text-white/20 text-[10px] uppercase font-bold mt-2">Haz clic en "Añadir Pregunta" para comenzar</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ExamEditor;
