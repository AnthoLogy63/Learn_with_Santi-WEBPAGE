import React from 'react';
import { Trash2, ChevronUp, ChevronDown, Clock, ImageIcon, Plus, HelpCircle } from 'lucide-react';
import { LocalQuestion, TipoPregunta, LocalOption, Competencia } from '@/api/examService';
import OptionEditor from './OptionEditor';

interface QuestionCardProps {
    question: LocalQuestion;
    index: number;
    isExpanded: boolean;
    tipoPreguntas: TipoPregunta[];
    allCompetencies: Competencia[];
    onToggleExpand: () => void;
    onDeleteQuestion: () => void;
    onUpdateQuestion: (data: Partial<LocalQuestion>, file?: File) => void;
    onUpdateOption: (opc_cod: string, data: Partial<LocalOption>) => void;
    onDeleteOption: (opc_cod: string) => void;
    onToggleCorrect: (opc_cod: string) => void;
    onAddOption: () => void;
}

const QuestionCard: React.FC<QuestionCardProps> = ({
    question: q,
    index,
    isExpanded,
    tipoPreguntas,
    onToggleExpand,
    onDeleteQuestion,
    onUpdateQuestion,
    onUpdateOption,
    onDeleteOption,
    onToggleCorrect,
    onAddOption,
    allCompetencies
}) => {
    const getImageUrl = (question: LocalQuestion) => {
        if (question.tempImageUrl) return question.tempImageUrl;
        if (!question.pre_fot) return null;
        
        // If it's already an absolute URL, return it
        if (typeof question.pre_fot === 'string' && (question.pre_fot.startsWith('http://') || question.pre_fot.startsWith('https://'))) {
            return question.pre_fot;
        }

        // Get API URL and handle potential trailing slashes
        const apiUrl = (import.meta.env.VITE_API_URL || '').replace('/api', '');
        const cleanApiUrl = apiUrl.endsWith('/') ? apiUrl.slice(0, -1) : apiUrl;
        
        // If it doesn't have /media/, add it
        let path = question.pre_fot;
        if (!path.startsWith('/media/') && !path.startsWith('media/')) {
            path = path.startsWith('/') ? `/media${path}` : `/media/${path}`;
        } else {
            path = path.startsWith('/') ? path : `/${path}`;
        }
        
        return `${cleanApiUrl}${path}`;
    };

    return (
        <div className="bg-white rounded-3xl overflow-hidden shadow-2xl transition-all border border-white/10">
            {/* Question Header */}
            <div
                className="p-4 md:p-6 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors"
                onClick={onToggleExpand}
            >
                <div className="flex items-center gap-4">
                    <div className="bg-[#001c4d] text-white h-8 w-8 rounded-xl flex items-center justify-center font-black text-xs shadow-md">
                        {index + 1}
                    </div>
                    <div>
                        <p className="font-bold text-[#001c4d] truncate max-w-[200px] md:max-w-md">{q.pre_tex}</p>
                        <div className="flex gap-3 items-center mt-1">
                            <span className="text-[9px] font-black uppercase tracking-widest text-[#001c4d]/60">{q.pre_pun} pts</span>
                            {q.com_cod && (
                                <span className="text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-500 border border-indigo-100">
                                    {allCompetencies.find(c => c.com_cod === q.com_cod)?.com_nom || q.com_cod}
                                </span>
                            )}
                            <span className="text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-md bg-[#001c4d]/5 text-[#001c4d]/40">
                                {tipoPreguntas.find(tp => tp.tip_pre_cod === q.tip_pre_cod)?.tip_pre_nom || 'Cargando...'}
                            </span>
                        </div>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={(e) => { e.stopPropagation(); onDeleteQuestion(); }}
                        className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    >
                        <Trash2 size={18} />
                    </button>
                    {isExpanded ? <ChevronUp className="text-[#001c4d]/40" /> : <ChevronDown className="text-[#001c4d]/40" />}
                </div>
            </div>

            {/* Expanded Content */}
            {isExpanded && (
                <div className="p-4 md:p-5 border-t border-slate-100 bg-slate-50/50 space-y-5 animate-in slide-in-from-top-4">
                    <div className="grid grid-cols-1 md:grid-cols-12 gap-5">
                        {/* Left: Metadata */}
                        <div className="md:col-span-8 space-y-4">
                            <div className="space-y-1.5">
                                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Enunciado de la pregunta</label>
                                <textarea
                                    value={q.pre_tex}
                                    onChange={(e) => onUpdateQuestion({ pre_tex: e.target.value })}
                                    rows={2}
                                    className="w-full bg-white border border-slate-200 rounded-2xl py-2 px-3 text-[#001c4d] focus:ring-2 focus:ring-[#001c4d]/20 focus:outline-none font-bold text-sm"
                                />
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                <div className="space-y-1.5">
                                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Tipo de Pregunta</label>
                                    <select
                                        value={q.tip_pre_cod || 1}
                                        onChange={(e) => onUpdateQuestion({ tip_pre_cod: parseInt(e.target.value) })}
                                        className="w-full bg-white border border-slate-200 rounded-xl py-2 px-3 text-[#001c4d] text-sm font-bold focus:ring-2 focus:ring-[#001c4d]/20 outline-none"
                                    >
                                        {tipoPreguntas.map(tp => (
                                            <option key={tp.tip_pre_cod} value={tp.tip_pre_cod}>
                                                {tp.tip_pre_nom}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Puntos</label>
                                    <input
                                        type="number"
                                        value={q.pre_pun}
                                        onChange={(e) => onUpdateQuestion({ pre_pun: parseInt(e.target.value) || 0 })}
                                        className="w-full bg-white border border-slate-200 rounded-xl py-2.5 px-3 text-[#001c4d] text-sm font-bold"
                                    />
                                </div>
                                
                                <div className="flex flex-col sm:flex-row gap-4 sm:col-span-2 items-end">
                                    <div className="flex-1 space-y-1.5 w-full">
                                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Tema / Competencia</label>
                                        <select
                                            value={q.com_cod || ""}
                                            onChange={(e) => onUpdateQuestion({ com_cod: e.target.value })}
                                            className="w-full bg-white border border-slate-200 rounded-xl py-2 px-3 text-[#001c4d] text-sm font-bold focus:ring-2 focus:ring-[#001c4d]/20 outline-none"
                                        >
                                            <option value="">Sin competencia</option>
                                            {allCompetencies.map(comp => (
                                                <option key={comp.com_cod} value={comp.com_cod}>
                                                    {comp.com_nom}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                    <div className="space-y-1.5 w-full sm:w-28">
                                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest text-right block pr-2">Tiempo</label>
                                        <div className="relative">
                                            <Clock className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
                                            <input
                                                type="number"
                                                value={q.pre_tie}
                                                onChange={(e) => onUpdateQuestion({ pre_tie: parseInt(e.target.value) || 0 })}
                                                className="w-full bg-white border border-slate-200 rounded-xl py-2 pl-9 pr-2 text-[#001c4d] text-sm font-bold text-center"
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Right: Image Upload */}
                        <div className="md:col-span-4 space-y-2">
                            <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Guía Visual (Opcional)</label>
                            <div className="relative aspect-video rounded-2xl border-2 border-dashed border-slate-200 bg-white flex flex-col items-center justify-center overflow-hidden group">
                                {getImageUrl(q) ? (
                                    <>
                                        <img src={getImageUrl(q)!} alt="Guia" className="w-full h-full object-cover" />
                                        <div className="absolute inset-0 bg-[#001c4d]/60 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                            <label className="bg-white text-[#001c4d] px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest cursor-pointer">Cambiar Foto</label>
                                        </div>
                                    </>
                                ) : (
                                    <>
                                        <ImageIcon className="h-8 w-8 text-slate-300 mb-2" />
                                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Subir Imagen</span>
                                    </>
                                )}
                                <input
                                    type="file"
                                    accept="image/*"
                                    className="absolute inset-0 opacity-0 cursor-pointer"
                                    onChange={(e) => {
                                        const file = e.target.files?.[0];
                                        if (file) onUpdateQuestion({}, file);
                                    }}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Answers Section - Only if NOT Open Question (type 2) */}
                    {q.tip_pre_cod !== 2 ? (
                        <OptionEditor
                            pre_cod={q.pre_cod}
                            tip_pre_cod={q.tip_pre_cod}
                            options={q.options}
                            onUpdateOption={onUpdateOption}
                            onDeleteOption={onDeleteOption}
                            onToggleCorrect={onToggleCorrect}
                            onAddOption={onAddOption}
                        />
                    ) : (
                        <div className="space-y-4">
                            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
                                <h4 className="text-[11px] font-black text-amber-600 uppercase tracking-widest">Pregunta Abierta</h4>
                            </div>
                            <div className="bg-amber-50 border border-amber-100 p-6 rounded-2xl">
                                <p className="text-xs text-amber-800 leading-relaxed font-medium">
                                    Esta pregunta no tiene opciones fijas. El usuario verá un cuadro de texto para escribir su respuesta. 
                                    Se marcará como completada una vez el usuario escriba algo.
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default QuestionCard;
