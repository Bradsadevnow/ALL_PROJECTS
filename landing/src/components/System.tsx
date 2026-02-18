import { Shield, Database, Layers, Network } from 'lucide-react';
import { Section } from './ui/Section';

const SystemCard = ({ icon: Icon, title, points, vibe }: { icon: any, title: string, points: string[], vibe: 'tech' | 'normal' | 'brainrot' }) => (
    <div className={`group relative p-6 border transition-all duration-500 overflow-hidden ${vibe === 'brainrot' ? 'border-white lisa-frank-bg shadow-xl scale-105 animate-vibrate-slow' : 'border-violet/20 bg-void/80 backdrop-blur-sm hover:border-violet/50'}`}>
        {/* Hover Gradient Background */}
        <div className={`absolute inset-0 transition-opacity duration-500 ${vibe === 'brainrot' ? 'opacity-30 intense-glitter' : 'bg-gradient-to-br from-violet/5 to-transparent opacity-0 group-hover:opacity-100'}`} />

        <div className="relative z-10 space-y-4">
            <div className={`w-12 h-12 flex items-center justify-center rounded-sm transition-all duration-300 ${vibe === 'brainrot' ? 'bg-white/20 border-white' : 'bg-violet/10 border-violet/30 group-hover:border-violet/50 group-hover:bg-violet/10'}`}>
                <Icon className={`transition-colors duration-300 ${vibe === 'brainrot' ? 'text-white' : 'text-violet group-hover:text-ethereal'}`} size={24} />
            </div>

            <h3 className={`text-xl font-bold font-mono tracking-tight transition-colors ${vibe === 'brainrot' ? 'text-white drop-shadow-md font-black italic' : 'text-white'}`}>{vibe === 'brainrot' ? title.toUpperCase() : title}</h3>

            <ul className="space-y-3">
                {points.map((point, i) => (
                    <li key={i} className={`text-sm flex items-start gap-3 transition-colors ${vibe === 'brainrot' ? 'text-white font-black' : 'text-ethereal/60'}`}>
                        <span className={`w-1 h-1 rounded-full mt-2 transition-colors ${vibe === 'brainrot' ? 'bg-white' : 'bg-violet group-hover:bg-ethereal'}`} />
                        {point}
                    </li>
                ))}
            </ul>
        </div>
        {vibe === 'brainrot' && (
            <div className="absolute top-2 right-2 text-2xl animate-spin-slow">👹</div>
        )}
    </div>
);

export const System = ({ vibe }: { vibe: 'tech' | 'normal' | 'brainrot' }) => {
    return (
        <Section id="system" className="relative">
            {/* Background Tech Element */}
            <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] -z-10 blur-[100px] transition-opacity ${vibe === 'brainrot' ? 'opacity-20 intense-glitter' : 'bg-[radial-gradient(circle_at_center,rgba(107,70,193,0.1)_0%,transparent_70%)] opacity-5'}`} />

            <div className="text-center mb-16 space-y-4">
                <h2 className={`text-sm font-bold tracking-[0.3em] uppercase transition-colors ${vibe === 'brainrot' ? 'text-white animate-bounce' : 'text-violet'}`}>
                    {vibe === 'brainrot' ? "CURRENT_BRAINROT_MAXING" : "Current Implementation"}
                </h2>
                <h3 className={`text-4xl md:text-6xl font-black tracking-tighter transition-all ${vibe === 'brainrot' ? 'text-rainbow scale-125 drop-shadow-[0_0_50px_rgba(255,0,247,0.8)]' : 'text-white'}`}>
                    PROJECT <span className={vibe === 'brainrot' ? 'text-white' : 'text-transparent bg-clip-text bg-gradient-to-r from-violet to-ethereal'}>{vibe === 'brainrot' ? "GYATT" : "STEVE"}</span>
                </h3>
                <p className={`font-mono transition-colors ${vibe === 'brainrot' ? 'text-white font-black text-xl animate-glitch' : 'text-ethereal/50'}`}>
                    {vibe === 'brainrot'
                        ? "SKIBIDI STATELESS VECTOR ENTITY // BRAINROT V.69.4.20"
                        : "Stateful Tool-Enabled Vector Entity // Runtime Version 0.9.4"
                    }
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <SystemCard
                    icon={Shield}
                    title={vibe === 'brainrot' ? "ABSOLUTE_AURA" : "Authoritative State"}
                    vibe={vibe}
                    points={vibe === 'brainrot' ? [
                        "DETERMINISTIC GYATT.",
                        "NO MID SLOP ALLOWED.",
                        "SCHEMA-RIZZ ACTIVE.",
                        "COMMIT OR GET MOGGED."
                    ] : [
                        "Explicit state transitions.",
                        "Gated memory writes.",
                        "Schema-constrained execution.",
                        "Zero silent mutation."
                    ]}
                />
                <SystemCard
                    icon={Database}
                    title={vibe === 'brainrot' ? "RIZZ_VAULT" : "Stratified Memory"}
                    vibe={vibe}
                    points={vibe === 'brainrot' ? [
                        "CONTEXT MAXING 👹",
                        "MEMORY WITH RIZZ.",
                        "VECTOR ISOLATION W."
                    ] : [
                        "Ephemeral behavioral context.",
                        "Committed factual long-term store.",
                        "Semantic vs. Tonal vector isolation."
                    ]}
                />
                <SystemCard
                    icon={Layers}
                    title={vibe === 'brainrot' ? "SLAY_CYCLES" : "Consolidation Cycles"}
                    vibe={vibe}
                    points={vibe === 'brainrot' ? [
                        "BRAINROT COMPRESSION 👺",
                        "DETERMINISTIC W'S.",
                        "NO CAP ACCUMULATION."
                    ] : [
                        "Context compression algorithms.",
                        "Deterministic thread reconstruction.",
                        "Preventing runaway accumulation."
                    ]}
                />
                <SystemCard
                    icon={Network}
                    title={vibe === 'brainrot' ? "GOAT_ORCHESTRATION" : "Deterministic Orchestration"}
                    vibe={vibe}
                    points={vibe === 'brainrot' ? [
                        "GEMINI MAXING 🦾",
                        "CRACKED EXECUTION.",
                        "OPPS CONTROLLED STRICTLY."
                    ] : [
                        "Genkit + Gemini 1.5 Pro.",
                        "Validated execution layers.",
                        "External dependencies strictly controlled."
                    ]}
                />
            </div>
        </Section>
    );
};
