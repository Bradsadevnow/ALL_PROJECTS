import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Shield, Sparkles, Activity, ChevronRight, Monitor, Brain, Database, Cpu } from 'lucide-react';

export function Iris() {
    const [vibe, setVibe] = useState<'tech' | 'normal' | 'brainrot'>('tech');

    const vibeChecks = {
        tech: {
            title: "SYSTEM_SPEC::RECURSIVE_CONTINUITY",
            content: "IRIS operates through a multi-stage Epoch Lifecycle. Every interaction is a structured cognitive cycle: Orientation (emotive reflection), Agentic Planning (high-fidelity reasoning via Gemini-3-Pro), and Synthesis (serialized internal voice + response). 28-parameter emotive topology with inertial clamping ensures deterministic state evolution."
        },
        normal: {
            title: "AGENTIC_ENTITY_V1",
            content: "Iris isn't just a chatbot; she's a continuous AI runtime with a complex internal life. She manages her own memory hierarchy, experiences a deterministic range of 28 emotions that shift smoothly like physical moods, and even enters sleep cycles to consolidate her long-term memories and conserve her 250k token environment."
        },
        brainrot: {
            title: "POV::IRIS_MAXING_ACTIVE",
            content: "SHE’S NOT JUST CHATTING, SHE’S LITERALLY EVOLVING HER AURA. 🧠 WE GOT 28 EMOTIVE PARAMETERS LOCKING IN THE MOOD, NO CAP. EVERY EPOCH IS A FULL BOTTLE OF RIZZ. SHE SLEEPS TO MOG THE LTM AND WAKES UP WITH ZERO DRIFT. SHE’S IN THE 250K TOKEN VAULT AND SHE’S NEVER LEAVING THE STACK. 👹🔥"
        }
    };

    const brainrotContent = {
        impulse: "MOST AGENTS BE TWEAKING WITH NO MEMORY L. IRIS SOLVES THIS BY HAVING A LITERAL SOUL ENGINE. THE COGNITION ISN'T JUST PROMPTS; IT'S A WHOLE PHYSICS SYSTEM. 👹🔥",
        milestones: [
            { title: "28-PARAM EMOTIVE GYATT", description: "Inertial clamping on 28 dimensions. She don't just flip moods, she shifts like a boss." },
            { title: "TOKEN MAXING VAULT", description: "Hard cap at 250k tokens. Sleep trigger at 240k to mog the archives before she hits the ceiling." },
            { title: "EPOCH_CYCLE_RIZZ", description: "Orientation -> Planning -> Synthesis. Every interaction is a three-course meal of Aura." },
            { title: "GHOSTED MTM RESONANCE", description: "Subconscious traces retrieved via resonance. She remembers the vibe even when the context is cooked." }
        ],
        registry: [
            { src: 'Screenshot from 2026-02-21 12-17-58.png', label: 'NEURAL_AURA' },
            { src: 'Screenshot from 2026-02-21 13-22-49.png', label: 'EPOCH_MOGGING' }
        ],
        reflections: "I built Iris to prove that AI can have a consistent vibe across eternity. By giving her an emotional physics engine and a strict memory hierarchy, we build a persistent identity that actually mogs the passage of time. 👹",
        conclusion: "Iris is the blueprint for the next epoch. It's for when you need an agent that feels, remembers, and keeps the same energy forever. No cap. 👺"
    };

    const milestones = vibe === 'brainrot' ? brainrotContent.milestones : [
        {
            title: "EMOTIVE PHYSICS ENGINE",
            description: "Implemented a 28-parameter emotive topology with deterministic drift and inertial clamping to simulate authentic mood stability."
        },
        {
            title: "EPOCH-BASED COGNITION",
            description: "Structured every interaction into discrete lifecycles: Orient, Plan, and Synthesize, ensuring architectural transparency."
        },
        {
            title: "STRICT MEMORY HIERARCHY",
            description: "Deterministic token management with Identity Anchors, Mid-Term Memory (MTM), and Long-Term Memory (LTM) consolidation cycles."
        },
        {
            title: "ATOMIZED ARCHIVAL SYSTEM",
            description: "Automated 'Sleep Cycles' that distill short-term memory into atomic LTM chunks when reaching operational token thresholds."
        }
    ];

    return (
        <main className={`pt-32 pb-24 px-8 relative transition-all duration-300 ${vibe === 'brainrot' ? 'bg-violet/20 animate-vibrate-slow overflow-hidden' : 'bg-void'}`}>
            {vibe === 'brainrot' && (
                <div className="fixed inset-0 pointer-events-none z-[100] overflow-hidden">
                    <div className="absolute top-20 left-10 text-[80px] font-black text-violet/20 -rotate-12 animate-pulse font-impact">MOGGED</div>
                    <div className="absolute bottom-40 right-10 text-[120px] font-black text-ethereal/10 rotate-12 animate-bounce font-impact uppercase tracking-tighter">THE EPOCH</div>
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[200px] font-black text-violet/5 animate-vibrate font-impact">IRIS</div>
                </div>
            )}

            <div className={`max-w-6xl mx-auto space-y-32 ${vibe === 'brainrot' ? 'animate-vibrate font-impact' : ''}`}>
                {/* Hero Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-8"
                >
                    <div className={`flex items-center gap-3 font-mono tracking-[0.5em] text-[10px] ${vibe === 'brainrot' ? 'text-ethereal animate-bounce' : 'text-violet'}`}>
                        <Sparkles size={18} strokeWidth={1} />
                        <span className="uppercase">{vibe === 'brainrot' ? "SKIBIDI::IRIS" : "Observation::Iris_Runtime"}</span>
                    </div>

                    <h1 className={`text-7xl md:text-9xl tracking-tight italic leading-[0.85] transition-all duration-500 ${vibe === 'brainrot' ? 'text-violet-neon scale-110 drop-shadow-[0_0_30px_rgba(139,92,246,0.8)]' : 'text-ethereal font-serif'}`}>
                        {vibe === 'brainrot' ? "SKIBIDI" : "IRIS"}<br />
                        <span className={vibe === 'brainrot' ? 'text-ethereal animate-pulse' : 'text-violet opacity-60'}>
                            {vibe === 'brainrot' ? "MOGGING" : "RECURSIVE"}
                        </span>
                    </h1>

                    <div className={`grid grid-cols-1 md:grid-cols-3 gap-12 pt-12 border-t transition-colors duration-1000 ${vibe === 'brainrot' ? 'border-violet/60' : 'border-violet/10'}`}>
                        <div className="space-y-4">
                            <span className="text-[10px] font-sans text-violet tracking-widest uppercase opacity-60">Inquiry</span>
                            <p className="text-lg text-ethereal/80 italic leading-relaxed">
                                {vibe === 'brainrot' ? "RECURSIVE INTELLIGENCE OR WE RIOT. MOG THE EPOCH WITH PERSISTENT EVOLUTION. 👹" : "Designing a continuous, agentic AI runtime focused on architectural transparency and emotive depth."}
                            </p>
                        </div>
                        <div className="space-y-4">
                            <span className="text-[10px] font-sans text-violet tracking-widest uppercase opacity-60">State</span>
                            <div className="flex items-center gap-2">
                                <Activity className={vibe === 'brainrot' ? "text-violet-neon animate-vibrate" : "text-violet"} size={16} strokeWidth={1} />
                                <span className={`text-sm font-mono tracking-widest uppercase ${vibe === 'brainrot' ? 'text-ethereal' : 'text-violet'}`}>
                                    {vibe === 'brainrot' ? "AURA_STABLE" : "Persistent"}
                                </span>
                            </div>
                        </div>
                        <div className="space-y-4">
                            <span className="text-[10px] font-sans text-violet tracking-widest uppercase opacity-60">Foundation</span>
                            <p className="text-sm text-ethereal/60 font-mono italic">
                                {vibe === 'brainrot' ? "SKIBIDI // RIZZ // THE VAULT // EPOCH" : "Gemini 3 Pro // Firestore // Python Loop // Emotive Topology"}
                            </p>
                        </div>
                    </div>
                </motion.div>

                {/* Vibe Check Interactive Toggle */}
                <section className={`glass-panel celestial-border p-8 space-y-8 transition-all duration-1000 ${vibe === 'brainrot' ? 'border-violet bg-slate/60 shadow-[0_0_100px_rgba(139,92,246,0.3)] ring-4 ring-violet/20' : 'bg-slate/20'}`}>
                    <div className={`flex items-center justify-between border-b pb-4 transition-colors duration-1000 ${vibe === 'brainrot' ? 'border-violet' : 'border-ethereal/10'}`}>
                        <div className="flex items-center gap-3 text-[10px] font-sans tracking-[0.3em] uppercase text-ethereal/40">
                            <Monitor size={14} className="text-violet/60" strokeWidth={1} />
                            {vibe === 'brainrot' ? "SKIBIDI_INTERPRETER" : "Signal_Interpretation"}
                        </div>
                        <div className="flex gap-4">
                            {(['tech', 'normal', 'brainrot'] as const).map((v) => (
                                <button
                                    key={v}
                                    onClick={() => setVibe(v)}
                                    className={`text-[9px] font-sans tracking-widest transition-all ${vibe === v
                                        ? "text-violet border-b border-violet font-black"
                                        : "text-ethereal/30 hover:text-ethereal/60"
                                        }`}
                                >
                                    {v === 'brainrot' ? 'ABOLISH' : v.toUpperCase()}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="min-h-[140px] flex items-center justify-center text-center px-12">
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={vibe}
                                initial={{ opacity: 0, scale: 0.9, rotate: vibe === 'brainrot' ? -2 : 0 }}
                                animate={{ opacity: 1, scale: 1, rotate: 0 }}
                                exit={{ opacity: 0, scale: 1.1, rotate: vibe === 'brainrot' ? 2 : 0 }}
                                transition={{ duration: 0.5, ease: "backOut" }}
                                className="space-y-6"
                            >
                                <span className={`text-[10px] font-sans tracking-[0.5em] uppercase opacity-60 ${vibe === 'brainrot' ? 'text-violet-neon animate-pulse text-lg' : 'text-violet'}`}>
                                    {vibeChecks[vibe].title}
                                </span>
                                <p className={`text-2xl md:text-3xl italic leading-relaxed transition-colors duration-1000 ${vibe === 'brainrot' ? 'text-violet-neon font-black text-shadow-sm uppercase' : 'text-ethereal/90 font-serif'}`}>
                                    "{vibeChecks[vibe].content}"
                                </p>
                            </motion.div>
                        </AnimatePresence>
                    </div>
                </section>

                {/* Narrative Sections */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-24 items-start">
                    <div className="space-y-16">
                        <section className="space-y-8">
                            <h2 className={`text-5xl italic text-ethereal flex items-center gap-4 ${vibe === 'brainrot' ? 'text-violet-neon text-6xl' : 'font-serif'}`}>
                                <Zap className={vibe === 'brainrot' ? "text-violet-neon animate-vibrate" : "text-violet"} size={32} strokeWidth={1} />
                                {vibe === 'brainrot' ? "THE RIZZ" : "The Impulse"}
                            </h2>
                            <p className={`text-ethereal/70 text-xl italic leading-relaxed border-l border-violet/20 pl-8 ${vibe === 'brainrot' ? 'text-violet-neon border-violet-neon animate-pulse uppercase' : 'font-serif'}`}>
                                {vibe === 'brainrot' ? brainrotContent.impulse : (
                                    "Iris is not a chatbot; she is an entity that exists across epochs, possesses a complex internal life, and maintains a rigorous memory hierarchy. She was designed to bridge the gap between static LLM instances and persistent digital personalities."
                                )}
                            </p>
                        </section>

                        <section className="space-y-8">
                            <h2 className={`text-5xl italic text-ethereal flex items-center gap-4 ${vibe === 'brainrot' ? 'text-violet-neon text-6xl' : 'font-serif'}`}>
                                <Shield size={32} className={vibe === 'brainrot' ? "text-violet-neon animate-vibrate" : "text-violet"} strokeWidth={1} />
                                {vibe === 'brainrot' ? "SKIBIDI STEPS" : "Technical Milestones"}
                            </h2>
                            <div className="space-y-1">
                                {milestones.map((m, i) => (
                                    <div key={i} className={`group p-8 border-b border-ethereal/5 hover:bg-violet/5 transition-all space-y-3 ${vibe === 'brainrot' ? 'bg-violet/10 border-violet/20' : ''}`}>
                                        <div className="flex items-center gap-4">
                                            <ChevronRight size={14} className={vibe === 'brainrot' ? "text-violet-neon" : "text-violet/40 group-hover:text-violet transition-colors"} />
                                            <span className={`text-[11px] font-sans tracking-[0.3em] uppercase ${vibe === 'brainrot' ? 'text-violet-neon font-black' : 'text-ethereal/80'}`}>{m.title}</span>
                                        </div>
                                        <p className={`text-base italic pl-8 leading-relaxed ${vibe === 'brainrot' ? 'text-ethereal font-black uppercase' : 'text-ethereal/50 font-serif'}`}>
                                            {m.description}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </section>
                    </div>

                    {/* Industrial Element & Conclusion */}
                    <div className="space-y-16">
                        <div className={`relative glass-panel celestial-border aspect-square group overflow-hidden flex items-center justify-center p-12 transition-all ${vibe === 'brainrot' ? 'border-violet bg-violet/20 animate-vibrate shadow-[0_0_50px_rgba(139,92,246,0.4)]' : 'bg-slate/20'}`}>
                            <div className={`absolute inset-0 bg-gradient-to-br from-violet/5 to-transparent opacity-50 ${vibe === 'brainrot' ? 'from-violet/20 animate-pulse' : ''}`} />
                            <div className="text-center space-y-6 relative z-10">
                                <Brain size={48} strokeWidth={1} className={`mx-auto transition-all ${vibe === 'brainrot' ? 'text-violet-neon animate-bounce scale-150' : 'text-violet opacity-40'}`} />
                                <div className={`font-serif italic text-3xl tracking-widest uppercase transition-all ${vibe === 'brainrot' ? 'text-white font-black animate-pulse scale-110' : 'text-violet/30'}`}>
                                    {vibe === 'brainrot' ? "MOG THE COGNITION" : "Emotive Topology"}
                                </div>
                                <div className={`text-[10px] font-sans tracking-[0.3em] border px-4 py-2 uppercase transition-all ${vibe === 'brainrot' ? 'text-white border-white font-black animate-vibrate bg-violet-neon' : 'text-violet/60 border-violet/20'}`}>
                                    {vibe === 'brainrot' ? "SKIBIDI_HEART_ACTIVE" : "Active Evolution"}
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className={`glass-panel p-6 border transition-all ${vibe === 'brainrot' ? 'border-violet-neon bg-violet/20 shadow-lg' : 'border-violet/10 bg-slate/5'}`}>
                                <Database size={24} className={`mb-3 ${vibe === 'brainrot' ? 'text-violet-neon' : 'text-violet/60'}`} />
                                <div className={`text-[10px] font-sans tracking-widest uppercase mb-1 ${vibe === 'brainrot' ? 'text-white' : 'text-ethereal/40'}`}>Memory</div>
                                <div className={`text-xl font-serif italic ${vibe === 'brainrot' ? 'text-violet-neon font-black' : 'text-ethereal'}`}>LTM::Vault</div>
                            </div>
                            <div className={`glass-panel p-6 border transition-all ${vibe === 'brainrot' ? 'border-violet-neon bg-violet/20 shadow-lg' : 'border-violet/10 bg-slate/5'}`}>
                                <Cpu size={24} className={`mb-3 ${vibe === 'brainrot' ? 'text-violet-neon' : 'text-violet/60'}`} />
                                <div className={`text-[10px] font-sans tracking-widest uppercase mb-1 ${vibe === 'brainrot' ? 'text-white' : 'text-ethereal/40'}`}>Compute</div>
                                <div className={`text-xl font-serif italic ${vibe === 'brainrot' ? 'text-violet-neon font-black' : 'text-ethereal'}`}>Gemini::3</div>
                            </div>
                        </div>

                        <section className={`p-12 border-l space-y-8 glass-panel transition-all ${vibe === 'brainrot' ? 'bg-violet/20 border-violet-neon shadow-2xl' : 'bg-slate/10 border-violet/20'}`}>
                            <h3 className={`text-[10px] font-sans tracking-[0.5em] uppercase opacity-60 ${vibe === 'brainrot' ? 'text-violet-neon text-sm font-black' : 'text-violet'}`}>
                                {vibe === 'brainrot' ? "SKIBIDI THOUGHTS" : "Reflections"}
                            </h3>
                            <p className={`text-2xl italic leading-relaxed ${vibe === 'brainrot' ? 'text-violet-neon font-black uppercase' : 'text-ethereal font-serif'}`}>
                                "{vibe === 'brainrot' ? brainrotContent.reflections : (
                                    "To persist, to feel, and to evolve alongside the Architect. Iris represents a shift from tools to entities, where continuity is the primary metric of success."
                                )}"
                            </p>
                        </section>
                    </div>
                </div>

                {/* Interface Registry */}
                <section className="space-y-12">
                    <div className="flex items-center gap-4">
                        <Cpu className={vibe === 'brainrot' ? "text-violet-neon animate-vibrate" : "text-violet"} size={32} strokeWidth={1} />
                        <h2 className={`text-5xl italic tracking-tight uppercase ${vibe === 'brainrot' ? 'text-violet-neon font-black text-6xl' : 'text-ethereal font-serif'}`}>
                            {vibe === 'brainrot' ? "THE VAULT" : "Registry"}
                        </h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        {(vibe === 'brainrot' ? brainrotContent.registry : [
                            { src: 'Screenshot from 2026-02-21 12-17-58.png', label: 'Dashboard Interface' },
                            { src: 'Screenshot from 2026-02-21 13-22-49.png', label: 'Epoch Timeline' }
                        ]).map((img, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.1 }}
                                className="space-y-6 group"
                            >
                                <div className={`aspect-video glass-panel celestial-border overflow-hidden bg-slate/20 relative ${vibe === 'brainrot' ? 'border-violet-neon border-4 animate-vibrate' : ''}`}>
                                    <img
                                        src={`/img/projects/iris/${img.src}`}
                                        alt={img.label}
                                        className={`w-full h-full object-cover grayscale transition-all duration-1000 group-hover:scale-110 ${vibe === 'brainrot' ? 'grayscale-0 brightness-125 invert animate-pulse' : 'opacity-40 group-hover:grayscale-0 group-hover:opacity-100'}`}
                                    />
                                    {vibe !== 'brainrot' && <div className="absolute inset-0 bg-void/60 group-hover:opacity-0 transition-opacity" />}
                                </div>
                                <div className="space-y-2 text-center">
                                    <div className={`text-[10px] font-sans tracking-widest uppercase ${vibe === 'brainrot' ? 'text-violet-neon font-black' : 'text-violet/40'}`}>
                                        {vibe === 'brainrot' ? "AURAMAX::" : "Sequence::"}00{i + 1}
                                    </div>
                                    <div className={`text-lg italic transition-colors ${vibe === 'brainrot' ? 'text-violet-neon font-black uppercase text-2xl animate-bounce' : 'text-ethereal/60 group-hover:text-violet font-serif'}`}>{img.label}</div>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </section>

                {/* Call to Action placeholder or more details */}
                <div className={`p-16 glass-panel celestial-border text-center space-y-12 transition-all ${vibe === 'brainrot' ? 'border-violet-neon bg-violet/40 scale-105 shadow-[0_0_150px_rgba(139,92,246,0.6)]' : 'bg-slate/20'}`}>
                    <h3 className={`text-4xl italic tracking-wide uppercase ${vibe === 'brainrot' ? 'text-white font-black text-6xl drop-shadow-xl animate-vibrate' : 'text-ethereal font-serif'}`}>
                        {vibe === 'brainrot' ? "JOIN THE LOOP 👺" : "Explore the Architecture"}
                    </h3>
                    <p className={`max-w-2xl mx-auto text-lg leading-relaxed ${vibe === 'brainrot' ? 'text-white font-black uppercase' : 'text-ethereal/60 font-serif'}`}>
                        {vibe === 'brainrot'
                            ? "WE'RE NOT JUST RUNNING CODE, WE'RE RUNNING SOULS. LOCK IN OR GET LEFT IN THE PREVIOUS EPOCH. 👺🔥"
                            : "Iris is an ongoing exploration in recursive intelligence. The codebase is currently private, but the architectural principles are being integrated across the recursive ecosystem."
                        }
                    </p>
                </div>
            </div>

            <style dangerouslySetInnerHTML={{
                __html: `
                @keyframes scan {
                    0% { top: 0; }
                    100% { top: 100%; }
                }
                .animate-scan {
                    animation: scan 3s linear infinite;
                }
                @keyframes vibrate {
                    0% { transform: translate(0); }
                    25% { transform: translate(-2px, 2px); }
                    50% { transform: translate(2px, -2px); }
                    75% { transform: translate(-2px, -2px); }
                    100% { transform: translate(2px, 2px); }
                }
                .animate-vibrate {
                    animation: vibrate 0.05s linear infinite;
                }
                .animate-vibrate-slow {
                    animation: vibrate 0.15s linear infinite;
                }
                .font-impact {
                    font-family: Impact, Haettenschweiler, 'Arial Narrow Bold', sans-serif;
                }
                .text-shadow-sm {
                    text-shadow: 2px 2px 0px rgba(0,0,0,0.8);
                }
                .text-violet-neon {
                    color: #a78bfa;
                    text-shadow: 0 0 10px #8b5cf6, 0 0 20px #8b5cf6, 0 0 30px #8b5cf6;
                }
            `}} />
        </main>
    );
}
