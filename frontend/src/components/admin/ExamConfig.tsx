import { useState, useEffect } from "react";
import { examService, Categoria, Competencia } from "@/api/examService";
import { Plus, Trash2, Loader2, AlertCircle, Minus } from "lucide-react";
import { toast } from "sonner";

interface ExamConfigProps {
    exa_cod: string;
    allCompetencies: Competencia[];
    onConfigChange?: (config: CategoryConfig[]) => void;
}

interface SelectedCompetence {
    com_cod: string;
    num_preguntas: number;
}

export interface CategoryConfig {
    cat_cod: string;
    competencies: SelectedCompetence[];
}

const ExamConfig = ({ exa_cod, allCompetencies, onConfigChange }: ExamConfigProps) => {
    const [allCategories, setAllCategories] = useState<Categoria[]>([]);
    const [selectedCategories, setSelectedCategories] = useState<CategoryConfig[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchInitialData();
    }, [exa_cod]);

    // Emitir cambios al padre cada vez que selectedCategories cambie
    useEffect(() => {
        if (onConfigChange) {
            onConfigChange(selectedCategories);
        }
    }, [selectedCategories]);

    const fetchInitialData = async () => {
        setLoading(true);
        try {
            const [cats, config] = await Promise.all([
                examService.getCategorias(),
                examService.getExamConfig(exa_cod)
            ]);
            setAllCategories(cats);
            setSelectedCategories(config || []);
        } catch (error) {
            console.error("Error fetching config data:", error);
            toast.error("Error al cargar categorías y competencias");
        } finally {
            setLoading(false);
        }
    };

    const handleAddCategory = () => {
        if (selectedCategories.length >= allCategories.length) return;
        
        const availableCat = allCategories.find(c => !selectedCategories.some(sc => sc.cat_cod === c.cat_cod));
        if (availableCat) {
            setSelectedCategories([...selectedCategories, { cat_cod: availableCat.cat_cod, competencies: [] }]);
        }
    };

    const handleRemoveCategory = (cat_cod: string) => {
        setSelectedCategories(selectedCategories.filter(c => c.cat_cod !== cat_cod));
    };

    const handleAddCompetence = (cat_cod: string) => {
        const cat = selectedCategories.find(c => c.cat_cod === cat_cod);
        if (!cat) return;
        
        const availableComp = allCompetencies.find(c => !cat.competencies.some(sc => sc.com_cod === c.com_cod));
        if (availableComp) {
            const updated = selectedCategories.map(c => 
                c.cat_cod === cat_cod 
                ? { ...c, competencies: [...c.competencies, { com_cod: availableComp.com_cod, num_preguntas: 5 }] }
                : c
            );
            setSelectedCategories(updated);
        }
    };

    const handleUpdateCompetence = (cat_cod: string, com_cod: string, num: number) => {
        const updated = selectedCategories.map(c => 
            c.cat_cod === cat_cod 
            ? { 
                ...c, 
                competencies: c.competencies.map(comp => 
                    comp.com_cod === com_cod ? { ...comp, num_preguntas: num } : comp
                ) 
              }
            : c
        );
        setSelectedCategories(updated);
    };

    const handleRemoveCompetence = (cat_cod: string, com_cod: string) => {
        const updated = selectedCategories.map(c => 
            c.cat_cod === cat_cod 
            ? { ...c, competencies: c.competencies.filter(comp => comp.com_cod !== com_cod) }
            : c
        );
        setSelectedCategories(updated);
    };

    if (loading) return <div className="flex justify-center p-8"><Loader2 className="animate-spin text-white" /></div>;

    return (
        <section className="bg-white/5 border border-white/10 rounded-3xl p-6 md:p-8 space-y-6">
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-3">
                    <div className="h-10 w-10 bg-indigo-500/20 rounded-2xl flex items-center justify-center text-indigo-400">
                        <AlertCircle size={20} />
                    </div>
                    <div>
                        <h3 className="text-white font-black uppercase tracking-widest text-sm">Configuración del Examen</h3>
                        <p className="text-white/40 text-[10px] uppercase font-bold">Gestión de categorías y competencias</p>
                    </div>
                </div>
                <button 
                    onClick={handleAddCategory}
                    className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-xl border border-white/20 transition-all text-[10px] font-black uppercase tracking-widest flex items-center gap-2"
                >
                    <Plus size={16} />
                    Asignar Categoría
                </button>
            </div>

            <div className="space-y-4">
                {selectedCategories.map((catConfig) => (
                    <div key={catConfig.cat_cod} className="bg-white/5 border border-white/10 rounded-2xl p-4 space-y-4">
                        <div className="flex justify-between items-center border-b border-white/5 pb-3">
                            <div className="flex items-center gap-4 text-white">
                                <span className="text-[10px] font-black uppercase text-white/40">Categoría:</span>
                                <select 
                                    value={catConfig.cat_cod}
                                    onChange={(e) => {
                                        const updated = selectedCategories.map(c => 
                                            c.cat_cod === catConfig.cat_cod ? { ...c, cat_cod: e.target.value } : c
                                        );
                                        setSelectedCategories(updated);
                                    }}
                                    className="bg-transparent border-none focus:ring-0 font-black uppercase text-sm"
                                >
                                    {allCategories
                                        .filter(c => c.cat_cod === catConfig.cat_cod || !selectedCategories.some(sc => sc.cat_cod === c.cat_cod))
                                        .map(c => (
                                            <option key={c.cat_cod} value={c.cat_cod} className="bg-[#001c4d]">{c.cat_nom}</option>
                                        ))}
                                </select>
                            </div>
                            <button onClick={() => handleRemoveCategory(catConfig.cat_cod)} className="text-red-400 hover:text-red-300 p-1">
                                <Trash2 size={16} />
                            </button>
                        </div>

                        <div className="space-y-3">
                            <div className="flex justify-between items-center">
                                <span className="text-[9px] font-black uppercase tracking-widest text-white/30">Distribución por Competencia</span>
                                <button 
                                    onClick={() => handleAddCompetence(catConfig.cat_cod)}
                                    className="text-indigo-400 hover:text-indigo-300 text-[10px] font-black uppercase tracking-widest flex items-center gap-1"
                                >
                                    <Plus size={14} />
                                    Añadir Competencia
                                </button>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                {catConfig.competencies.map((comp) => (
                                    <div key={comp.com_cod} className="group relative flex flex-wrap items-center justify-center md:justify-start gap-3 bg-white/5 hover:bg-white/10 p-2.5 rounded-2xl border border-white/10 transition-all duration-300">
                                        <div className="flex-1 min-w-[140px]">
                                            <select 
                                                value={comp.com_cod}
                                                onChange={(e) => {
                                                    const updated = catConfig.competencies.map(cc => 
                                                        cc.com_cod === comp.com_cod ? { ...cc, com_cod: e.target.value } : cc
                                                    );
                                                    const updatedCats = selectedCategories.map(c => 
                                                        c.cat_cod === catConfig.cat_cod ? { ...c, competencies: updated } : c
                                                    );
                                                    setSelectedCategories(updatedCats);
                                                }}
                                                className="w-full bg-transparent border-none focus:ring-0 text-white text-[11px] font-bold py-1 leading-tight appearance-none truncate"
                                            >
                                                {allCompetencies.map(c => (
                                                    <option key={c.com_cod} value={c.com_cod} className="bg-[#001c4d]">{c.com_nom}</option>
                                                ))}
                                            </select>
                                        </div>
                                        
                                        <div className="flex items-center gap-1 bg-white/5 p-1 rounded-xl border border-white/5">
                                            <button 
                                                onClick={() => handleUpdateCompetence(catConfig.cat_cod, comp.com_cod, Math.max(0, comp.num_preguntas - 1))}
                                                className="w-6 h-6 flex items-center justify-center text-white/40 hover:text-white hover:bg-white/10 rounded-lg transition-all"
                                            >
                                                <Minus size={12} />
                                            </button>
                                            <input 
                                                type="number" 
                                                value={comp.num_preguntas}
                                                onChange={(e) => handleUpdateCompetence(catConfig.cat_cod, comp.com_cod, parseInt(e.target.value) || 0)}
                                                className="w-8 bg-transparent border-none focus:ring-0 text-white text-[11px] text-center font-black [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none p-0"
                                            />
                                            <button 
                                                onClick={() => handleUpdateCompetence(catConfig.cat_cod, comp.com_cod, comp.num_preguntas + 1)}
                                                className="w-6 h-6 flex items-center justify-center text-white/40 hover:text-white hover:bg-white/10 rounded-lg transition-all"
                                            >
                                                <Plus size={12} />
                                            </button>
                                        </div>

                                        <button 
                                            onClick={() => handleRemoveCompetence(catConfig.cat_cod, comp.com_cod)} 
                                            className="p-1.5 text-white/20 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-all"
                                            title="Eliminar Competencia"
                                        >
                                            <Trash2 size={14} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                ))}

                {selectedCategories.length === 0 && (
                    <div className="py-12 text-center bg-white/5 rounded-2xl border border-dashed border-white/20">
                        <p className="text-white/60 text-xs font-bold italic">No hay categorías asignadas a este examen.</p>
                    </div>
                )}
            </div>
        </section>
    );
};

export default ExamConfig;
