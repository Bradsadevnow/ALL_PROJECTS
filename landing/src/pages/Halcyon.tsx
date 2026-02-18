import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Heart, Brain, Activity, ChevronRight, Github, Monitor } from 'lucide-react';

export function Halcyon() {
    const [vibe, setVibe] = useState<'tech' | 'normal' | 'brainrot'>('tech');

    const vibeChecks = {
        tech: {
            title: "NEURO_SPEC::NAMED_VECTORS",
            content: "Implemented a neuro-inspired memory architecture using Qdrant's named vectors. Memory is split into 'content' (semantic/factual) and 'emotional' (tonal/affective) embedding spaces. Retrieval logic uses a weighted hybrid search to select memories that match both the factual context and the current emotional valence."
        },
        normal: {
            title: "MEMORY_WITH_FEELINGS",
            content: "Most AI remembers things like a search engine. Halcyon remembers things more like a person. It stores every memory twice: once for the facts, and once for how it felt at the time. When you talk to it, it looks for past experiences that match your current mood, not just your words."
        },
        brainrot: {
            title: "POV::VIBE_MAXING_ACTIVE",
            content: "WE’RE NOT JUST SEARCHING FOR KEYWORDS, GLAZER. 🧠 I BUILT A LITERAL HIPPOCAMPUS FOR THIS AGENT GYATT. IT USES DUAL VECTORS SO IT CAN RECALL MEMORIES BASED ON PURE RIZZ. IF YOU’RE CRASHING, IT REMEMBERS THE CRASH. IT’S NOT AN LLM; IT’S A PERMANENT VIBE LOOP. 👹🔥"
        }
    };

    const brainrotContent = {
        impulse: "MOST MEMORY SYSTEMS FOCUS ON 'WHAT.' HALCYON FOCUSES ON THE AURA. BY INTEGRATING EMOTIONAL VALENCE INTO THE RETRIEVAL LOOP, WE CREATE AGENTS THAT DEVELOP LITERAL PERSONALITIES. NO MID RECALLS. 👹🦾",
        milestones: [
            { title: "DUAL-RIZZ EMBEDDINGS", description: "Engineered a memory pipeline that generates two distinct vectors: one for the facts, one for the vibes. Absolute Aura." },
            { title: "HYBRID RETRIEVAL GYATT", description: "Custom retrieval algorithm in Qdrant that moggs factual search with emotional resonance. 👺" },
            { title: "NEURAL-MAPPED MOGGING", description: "Architecture modeled after brain structures: `cortex.py` (mogging), `hippocampus.py` (rizz), and `thalamus.py` (taxing)." },
            { title: "DYNAMIC AFFECTIVE PULSE", description: "The agent maintains a rolling 'Aura Score' that influences what it remembers and how it frames the response.👺" }
        ],
        reflections: "Halcyon represents a shift from agents that process data to agents that process the Grind. By giving the system an emotional 'sense', we allow it to navigate human interaction with a level of rizz that raw semantic search simply can't touch. 🦾",
        conclusion: "We're not building search engines. We're building digital identities with receipts for how they felt. No cap. 👹"
    };

    const milestones = vibe === 'brainrot' ? brainrotContent.milestones : [
        {
            title: "DUAL-PERSPECTIVE EMBEDDINGS",
            description: "Engineered a memory pipeline that generates two distinct embeddings per turn: one for semantic content and one for emotional tone."
        },
        {
            title: "HYBRID RETRIEVAL LOGIC",
            description: "Developed a custom retrieval algorithm in Qdrant that merges factual and emotional search results with a time-decay bias."
        },
        {
            title: "NEURAL-MAPPED ORCHESTRATION",
            description: "Architecture modeled after brain structures: `cortex.py` (processing), `hippocampus.py` (memory), and `thalamus.py` (routing)."
        },
        {
            title: "DYNAMIC AFFECTIVE STATE",
            description: "The agent maintains a rolling 'Emotional Pulse' that influences both what it remembers and how it frames its responses."
        }
    ];

    return (
        <main className={`pt-32 pb-24 px-8 relative overflow-hidden transition-all duration-300 ${vibe === 'brainrot' ? 'bg-violet/20 animate-vibrate-slow' : 'bg-void'}`}>
            {vibe === 'brainrot' && (
                <div className="fixed inset-0 pointer-events-none z-[100] overflow-hidden">
                    <div className="absolute top-20 left-10 text-[80px] font-black text-violet/20 -rotate-12 animate-pulse font-impact">RIZZED</div>
                    <div className="absolute bottom-40 right-10 text-[120px] font-black text-ethereal/10 rotate-12 animate-bounce font-impact uppercase tracking-tighter">HIPPOCAMPUS</div>
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[200px] font-black text-violet/5 animate-vibrate font-impact">HALCYON</div>
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
                        <Heart size={18} strokeWidth={1} />
                        <span className="uppercase">{vibe === 'brainrot' ? "SKIBIDI::AURA" : "Observation::Halcyon_Memory"}</span>
                    </div>

                    <h1 className={`text-7xl md:text-9xl tracking-tight italic leading-[0.85] transition-all duration-500 ${vibe === 'brainrot' ? 'text-violet-neon scale-110 drop-shadow-[0_0_30px_rgba(139,92,246,0.8)]' : 'text-ethereal font-serif'}`}>
                        {vibe === 'brainrot' ? "VIBE" : "HALCYON"}<br />
                        <span className={vibe === 'brainrot' ? 'text-ethereal animate-pulse' : 'text-violet opacity-60'}>
                            {vibe === 'brainrot' ? "MAXING" : "AFFECTIVE"}
                        </span>
                    </h1>

                    <div className={`grid grid-cols-1 md:grid-cols-3 gap-12 pt-12 border-t transition-colors duration-1000 ${vibe === 'brainrot' ? 'border-violet/60' : 'border-violet/10'}`}>
                        <div className="space-y-4">
                            <span className="text-[10px] font-sans text-violet tracking-widest uppercase opacity-60">Inquiry</span>
                            <p className="text-lg text-ethereal/80 italic leading-relaxed">
                                {vibe === 'brainrot' ? "MOG THE SEMANTIC SEARCH. WE RETRIEVIN' STRAIGHT VIBES ONLY. 👹" : "Bridging the gap between semantic retrieval and emotional resonance through named-vector memory architecture."}
                            </p>
                        </div>
                        <div className="space-y-4">
                            <span className="text-[10px] font-sans text-violet tracking-widest uppercase opacity-60">State</span>
                            <div className="flex items-center gap-2">
                                <Activity className={vibe === 'brainrot' ? "text-violet-neon animate-vibrate" : "text-violet"} size={16} strokeWidth={1} />
                                <span className={`text-sm font-mono tracking-widest uppercase ${vibe === 'brainrot' ? 'text-ethereal' : 'text-violet'}`}>
                                    {vibe === 'brainrot' ? "SKIBIDI_RECALL" : "Recall_Active"}
                                </span>
                            </div>
                        </div>
                        <div className="space-y-4">
                            <span className="text-[10px] font-sans text-violet tracking-widest uppercase opacity-60">Foundation</span>
                            <p className="text-sm text-ethereal/60 font-mono italic">
                                {vibe === 'brainrot' ? "QDRANT // RIZZ // VECTORS // GYATT" : "Qdrant // Named Vectors // Emotional Embeddings // Python"}
                            </p>
                        </div>
                    </div>
                </motion.div>

                {/* Vibe Check Interactive Toggle */}
                <section className={`glass-panel celestial-border p-8 space-y-8 transition-all duration-1000 ${vibe === 'brainrot' ? 'border-violet bg-slate/60 shadow-[0_0_100px_rgba(139,92,246,0.3)] ring-4 ring-violet/20' : 'bg-slate/20'}`}>
                    <div className={`flex items-center justify-between border-b pb-4 transition-colors duration-1000 ${vibe === 'brainrot' ? 'border-violet' : 'border-ethereal/10'}`}>
                        <div className="flex items-center gap-3 text-[10px] font-sans tracking-[0.3em] uppercase text-ethereal/40">
                            <Monitor size={14} className="text-violet/60" strokeWidth={1} />
                            {vibe === 'brainrot' ? "AURA_INTERPRETER" : "Signal_Interpretation"}
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
                                    "Most memory systems focus on 'What.' Halcyon focuses on 'How it felt.' By integrating emotional valence into the retrieval loop, we create agents that can maintain tonal consistency and develop something akin to a personality."
                                )}
                            </p>
                        </section>

                        <section className="space-y-8">
                            <h2 className={`text-5xl italic text-ethereal flex items-center gap-4 ${vibe === 'brainrot' ? 'text-violet-neon text-6xl' : 'font-serif'}`}>
                                <Brain size={32} className={vibe === 'brainrot' ? "text-violet-neon animate-vibrate" : "text-violet"} strokeWidth={1} />
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
                        <div className={`relative glass-panel celestial-border aspect-video group overflow-hidden flex items-center justify-center p-12 glow-violet transition-all ${vibe === 'brainrot' ? 'border-violet bg-violet/20 animate-vibrate' : 'bg-slate/20'}`}>
                            <div className={`absolute inset-0 bg-gradient-to-br from-violet/5 to-transparent opacity-50 ${vibe === 'brainrot' ? 'from-violet/20 animate-pulse' : ''}`} />
                            <div className={`absolute inset-0 h-[1px] top-0 animate-scan pointer-events-none ${vibe === 'brainrot' ? 'bg-white shadow-[0_0_20px_white]' : 'bg-violet/20'}`} />
                            <div className="text-center space-y-6 relative z-10">
                                <Activity size={48} strokeWidth={1} className={`mx-auto transition-all ${vibe === 'brainrot' ? 'text-violet-neon animate-bounce scale-150' : 'text-violet opacity-40'}`} />
                                <div className={`font-serif italic text-3xl tracking-widest uppercase transition-all ${vibe === 'brainrot' ? 'text-white font-black animate-pulse scale-110' : 'text-violet/30'}`}>
                                    {vibe === 'brainrot' ? "AURA LOOP" : "Affective Loop"}
                                </div>
                                <div className={`text-[10px] font-sans tracking-[0.3em] border px-4 py-2 uppercase transition-all ${vibe === 'brainrot' ? 'text-white border-white font-black animate-vibrate bg-violet-neon' : 'text-violet/60 border-violet/20'}`}>
                                    {vibe === 'brainrot' ? "GYATT_SYNTHESIS" : "Emotional Synthesis"}
                                </div>
                            </div>
                        </div>

                        <section className={`p-12 border-l space-y-8 glass-panel transition-all ${vibe === 'brainrot' ? 'bg-violet/20 border-violet-neon shadow-2xl' : 'bg-slate/10 border-violet/20'}`}>
                            <h3 className={`text-[10px] font-sans tracking-[0.5em] uppercase opacity-60 ${vibe === 'brainrot' ? 'text-violet-neon text-sm font-black' : 'text-violet'}`}>
                                {vibe === 'brainrot' ? "SKIBIDI THOUGHTS" : "Reflections"}
                            </h3>
                            <p className={`text-2xl italic leading-relaxed ${vibe === 'brainrot' ? 'text-violet-neon font-black uppercase' : 'text-ethereal font-serif'}`}>
                                "{vibe === 'brainrot' ? brainrotContent.reflections : (
                                    "Halcyon represents a shift from agents that process data to agents that process experience. By giving the system an emotional 'sense', we allow it to navigate human interaction with a level of nuance that raw semantic search simply can't touch."
                                )}"
                            </p>
                        </section>
                    </div>
                </div>

                {/* Call to Action */}
                <motion.div
                    whileInView={{ opacity: 1 }}
                    initial={{ opacity: 0 }}
                    className={`p-16 glass-panel celestial-border text-center space-y-12 transition-all ${vibe === 'brainrot' ? 'border-violet-neon bg-violet/40 scale-105 shadow-[0_0_150px_rgba(139,92,246,0.6)]' : 'bg-slate/20'}`}
                >
                    <h3 className={`text-4xl italic tracking-wide uppercase ${vibe === 'brainrot' ? 'text-white font-black text-6xl drop-shadow-xl animate-vibrate' : 'text-ethereal font-serif'}`}>
                        {vibe === 'brainrot' ? "JOIN THE CIRCLE 👹" : "Audit the Continuity"}
                    </h3>
                    <div className="flex justify-center flex-col items-center gap-8">
                        <a
                            href="https://github.com/Bradsadevnow/the_bottom_floor_of_an_ikea_where_they_build_stuff_or_pick_up_parts/tree/main/hal-main"
                            target="_blank"
                            rel="noopener noreferrer"
                            className={`px-12 py-5 border text-xs group transition-all flex items-center justify-center gap-4 tracking-[0.3em] uppercase ${vibe === 'brainrot' ? 'bg-white text-violet-neon border-white font-black animate-bounce scale-125 shadow-2xl' : 'border-violet/40 text-violet font-sans hover:bg-violet hover:text-void'}`}
                        >
                            <Github size={18} strokeWidth={1} className="group-hover:scale-110 transition-transform" />
                            {vibe === 'brainrot' ? "GITHUB_MOGGING" : "Repos_Strategy"}
                        </a>
                        {vibe === 'brainrot' && (
                            <div className="text-white font-black italic text-4xl animate-vibrate shadow-sm tracking-[0.5em] uppercase">
                                LOCK IN.
                            </div>
                        )}
                    </div>
                </motion.div>
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
