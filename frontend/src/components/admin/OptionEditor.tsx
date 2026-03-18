import React from 'react';
import { Trash2, CheckCircle, HelpCircle } from 'lucide-react';
import { LocalOption } from '@/api/examService';

interface OptionEditorProps {
    pre_cod: string;
    tip_pre_cod: number;
    options: LocalOption[];
    onUpdateOption: (opc_cod: string, data: Partial<LocalOption>) => void;
    onDeleteOption: (opc_cod: string) => void;
    onToggleCorrect: (opc_cod: string) => void;
    onAddOption: () => void;
}

const OptionEditor: React.FC<OptionEditorProps> = ({
    pre_cod,
    tip_pre_cod,
    options,
    onUpdateOption,
    onDeleteOption,
    onToggleCorrect,
    onAddOption
}) => {
    const activeOptions = options.filter(o => !o.isDeleted);

    return (
        <div className="space-y-3">
            <div className="flex justify-between items-center border-b border-slate-100 pb-2">
                <div className="flex items-center gap-3">
                    <h4 className="text-[11px] font-black text-[#001c4d] uppercase tracking-widest">Opciones de Respuesta</h4>
                    {tip_pre_cod === 3 && (
                        <span className="text-[9px] font-black text-indigo-500 bg-indigo-50 px-2 py-0.5 rounded-full uppercase">Formato: A | B</span>
                    )}
                    {tip_pre_cod === 4 && (
                        <span className="text-[9px] font-black text-amber-500 bg-amber-50 px-2 py-0.5 rounded-full uppercase">Fijo: V / F</span>
                    )}
                </div>
                
                {/* Hide add button for T/F (4) */}
                {tip_pre_cod !== 4 && (
                    <button
                        onClick={onAddOption}
                        className="flex items-center gap-1 text-[#001c4d] hover:bg-[#001c4d]/5 px-3 py-1 rounded-lg transition-all text-[10px] font-black uppercase tracking-widest border border-slate-200"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-plus"><path d="M12 5v14"/><path d="M5 12h14"/></svg>
                        Añadir Opción
                    </button>
                )}
            </div>

            <div className="grid grid-cols-1 gap-2">
                {activeOptions.map((opt) => (
                    <div key={opt.opc_cod} className={`group flex items-center gap-3 p-3 rounded-2xl border transition-all ${opt.opc_cor ? 'bg-emerald-50 border-emerald-200' : 'bg-white border-slate-100 hover:border-slate-300'}`}>
                        {/* IsCorrect Toggle - Hide for Relationship (3) */}
                        {tip_pre_cod !== 3 && (
                            <button
                                onClick={() => onToggleCorrect(opt.opc_cod)}
                                className={`h-8 w-8 rounded-full flex items-center justify-center transition-all ${opt.opc_cor ? 'bg-emerald-500 text-white shadow-lg' : 'bg-slate-100 text-slate-400 group-hover:bg-slate-200'}`}
                            >
                                <CheckCircle size={18} />
                            </button>
                        )}
                        
                        {/* Icon for Relationship just to keep visual balance */}
                        {tip_pre_cod === 3 && (
                            <div className="h-8 w-8 rounded-full bg-indigo-50 text-indigo-400 flex items-center justify-center">
                                <HelpCircle size={18} />
                            </div>
                        )}

                        {/* Option Text */}
                        {tip_pre_cod === 3 ? (
                            <div className="flex-1 flex items-center gap-2">
                                <input
                                    type="text"
                                    placeholder="Elemento A"
                                    value={opt.opc_tex.split('|')[0]?.trim() || ''}
                                    onChange={(e) => {
                                        const partB = opt.opc_tex.split('|')[1]?.trim() || '';
                                        onUpdateOption(opt.opc_cod, { opc_tex: `${e.target.value} | ${partB}` });
                                    }}
                                    className="w-1/2 bg-white/50 border border-slate-200 rounded-lg px-2 py-1 text-xs font-bold text-[#001c4d] focus:ring-1 focus:ring-indigo-300 outline-none"
                                />
                                <div className="h-4 w-px bg-slate-300" />
                                <input
                                    type="text"
                                    placeholder="Elemento B"
                                    value={opt.opc_tex.split('|')[1]?.trim() || ''}
                                    onChange={(e) => {
                                        const partA = opt.opc_tex.split('|')[0]?.trim() || '';
                                        onUpdateOption(opt.opc_cod, { opc_tex: `${partA} | ${e.target.value}` });
                                    }}
                                    className="w-1/2 bg-white/50 border border-slate-200 rounded-lg px-2 py-1 text-xs font-bold text-[#001c4d] focus:ring-1 focus:ring-indigo-300 outline-none"
                                />
                            </div>
                        ) : tip_pre_cod === 4 ? (
                            <div className="flex-1 flex items-center gap-2">
                                <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${opt.opc_tex.toLowerCase().includes('verdadero') ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
                                    {opt.opc_tex}
                                </span>
                                <span className="text-[10px] font-bold text-slate-400 italic">(Etiqueta Fija)</span>
                            </div>
                        ) : (
                            <input
                                type="text"
                                value={opt.opc_tex}
                                onChange={(e) => onUpdateOption(opt.opc_cod, { opc_tex: e.target.value })}
                                className={`flex-1 bg-transparent border-none focus:ring-0 text-sm font-bold p-1 ${opt.opc_cor ? 'text-emerald-900' : 'text-[#001c4d]'}`}
                            />
                        )}

                        {/* Delete Option - Hide for T/F (4) */}
                        {tip_pre_cod !== 4 && (
                            <button
                                onClick={() => onDeleteOption(opt.opc_cod)}
                                className="opacity-0 group-hover:opacity-100 p-2 text-slate-400 hover:text-red-500 transition-all"
                            >
                                <Trash2 size={16} />
                            </button>
                        )}
                    </div>
                ))}
                {activeOptions.length === 0 && (
                    <div className="py-6 text-center text-[#001c4d]/60 italic text-xs font-bold bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                        Sin opciones registradas.
                    </div>
                )}
            </div>
        </div>
    );
};

export default OptionEditor;
