import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Activity, ChevronRight, Github, Monitor, Database, GitBranch, Cpu, ShieldAlert } from 'lucide-react';

export function SharedWorkbench() {
    const [vibe, setVibe] = useState<'tech' | 'normal' | 'brainrot'>('tech');

    const vibeChecks = {
        tech: {
            title: "SYSTEM_SPEC::RUNTIME_DESIGN",
            content: "Implemented an epoch-authoritative runtime that converts stateless LLM responses into deterministic state transitions. Enforced schema-bound intent (InternalVoice) with atomic commit/abort lifecycle, append-only event ledger, tiered memory consolidation, and SSE-driven collaborative surface. Model proposes. Runtime governs.",
            isAggressive: false
        },
        normal: {
            title: "EXPLAIN_IT_TO_ME_LIKE_I'M_5",
            content: "I built a system that stops AI from quietly changing state or forgetting what it did. Every interaction is processed like a transaction — it either commits cleanly or rolls back. The model can suggest actions, but it doesn’t control the system. That prevents drift, tool hallucination, and memory corruption.",
            isAggressive: false
        },
        brainrot: {
            title: "POV::ABOLISH_THE_MID",
            content: "SKIBIDI STATE MANAGEMENT OR WE RIOT. 👹 y'all really out here glazing stateless LLMs like they aren't literal goldfish on a 128k context bender? 😭💀 big L. we're in the EPOCH era now. no more sneaky drift. you either COMMIT or you're a certified beta. model doesn't freestyle, it's strictly InternalVoice or it gets the ban hammer. tools? deterministic, not 'vibe-check' based. if it 404s, the whole timeline gets nuked. period. the ledger is a literal blood oath in JSONL format. replay your whole life from the womb. big payloads? redacted in the vault so your context isn't 17GB of brainrot metadata. LTM is cooked offline like a skibidi ritual — dreams and knowledge forged in the back while you're edge-maxing. plus minus rizz. we're so back. 👹🔥",
            isAggressive: true
        }
    };

    const brainrotContent = {
        impulse: "MOST AI APPS ARE STRAIGHT MID. THEY BE GASLIGHTING YOU WITH PROJECTIONS WHILE THE RUNTIME HAS ZERO AURA. SHARED_WORKBENCH IS THE FINAL BOSS: THE RUNTIME OWNS THE WHOLE SKIBIDI GYATT. THE MODEL SUGGESTS, THE LEDGER LOVES. NO CAP. 😭👹",
        milestones: [
            { title: "EPOCH AUTHORITATIVE GYATT", description: "IDLE → OPEN → COOKING → AURA COMMITTED | BETA ABORTED. Zero side effects or we riot." },
            { title: "SKIBIDI INTENT ENFORCEMENT", description: "InternalVoice or gtfo. Tools are deterministic, not interpretive glazers." },
            { title: "JSONL BLOOD OATH", description: "Every W epoch is a permanent receipt. Rehydrate from genesis or you're mid." },
            { title: "HUGE PAYLOAD REDACTION", description: "Big tool outputs get nuked in state to save your aura. Redacted in logs, valid in context." },
            { title: "MULTIVERSE MEMORY", description: "STM for the current grind. LTM for the identity arch, dream-maxing, and knowledge storage." }
        ],
        registry: [
            { src: 'Screenshot from 2026-02-12 09-16-26.png', label: 'NEURAL RIZZ' },
            { src: 'Screenshot from 2026-02-12 09-16-50.png', label: 'RUNTIME_AURA' },
            { src: 'Screenshot from 2026-02-12 09-17-13.png', label: 'EPOCH MOGGING' },
            { src: 'Screenshot from 2026-02-12 13-17-23.png', label: 'STATE_CONSOLIDATION' },
            { src: 'Screenshot from 2026-02-12 13-17-36.png', label: 'CORTEX MAXING' },
            { src: 'Screenshot from 2026-02-12 13-20-11.png', label: 'LEDGER_VAULT' },
            { src: 'Screenshot from 2026-02-12 13-20-33.png', label: 'COMMUNICATIONS_RIZZ' },
            { src: 'Screenshot from 2026-02-12 17-08-35.png', label: 'CONTROL GYATT' }
        ],
        modules: [
            { name: "Fanum Tax Link", desc: "Talk like a normie but the stream is watching. 👹" },
            { name: "State Forge", desc: "Model throws proposed edits like a Twitch dono. Approve or Get Luked." },
            { name: "The Brainrot Panel", desc: "Look at your own identity narrative, dream fragments, and trauma scars." },
            { name: "God Mode HUD", desc: "Nuke button. Kill switch. Infinite Aura control plane." }
        ],
        reflections: "Most AI products are just really good imaginary friends with zero rizz; this one is a straight-up courtroom where the judge is a skibidi toilet with receipts. 👹💀",
        conclusion: "Shared Workbench isn't for the vibes. It's for when the glazers fail and you need to know exactly who taxed the fanum tax. No cap. 👹"
    };

    const milestones = vibe === 'brainrot' ? brainrotContent.milestones : [
        {
            title: "EPOCH AUTHORITATIVE STATE MACHINE",
            description: "IDLE → OPEN → EXECUTING → COMMITTED | ABORTED. All user interactions resolve atomically. Failed epochs produce zero side effects."
        },
        {
            title: "STRUCTURED INTENT ENFORCEMENT",
            description: "Model responses are schema-bound (InternalVoice). Tool execution is deterministic, not interpretive."
        },
        {
            title: "APPEND-ONLY EVENT LEDGER",
            description: "Every committed epoch is logged to a JSONL continuity file. The system can be fully rehydrated from this ledger."
        },
        {
            title: "ETHEREAL PAYLOAD REDACTION",
            description: "Large tool outputs are available during execution but redacted in permanent logs to prevent context inflation."
        },
        {
            title: "TIERED MEMORY SYSTEM",
            description: "STM: Active continuity injection per epoch. LTM: Identity narrative, extracted knowledge, and dream synthesis via offline consolidation cycle."
        }
    ];

    const modules = vibe === 'brainrot' ? brainrotContent.modules : [
        { name: "Neural Link", desc: "The only place you still talk like normies (Chat + Event Stream)" },
        { name: "Deck Forge", desc: "Model throws proposed state changes at you like a Twitch dono. You either APPROVE or DENY like a medieval king." },
        { name: "Cortex", desc: "Straight up soul inspection panel. Look at your own identity narrative, dream fragments, knowledge scars." },
        { name: "Media HUD", desc: "Server-side panic button. Kill switch. Rewind. Nuke session. God mode control plane." }
    ];

    return (
        <main className={`pt-32 pb-24 px-8 relative transition-all duration-300 ${vibe === 'brainrot' ? 'bg-violet/20 animate-vibrate-slow overflow-hidden scale-[0.99] grayscale-0' : 'bg-void'}`}>
            {vibe === 'brainrot' && (
                <div className="fixed inset-0 pointer-events-none z-[100] overflow-hidden">
                    <div className="absolute top-20 left-10 text-[80px] font-black text-violet/20 -rotate-12 animate-pulse font-impact">SKIBIDI</div>
                    <div className="absolute bottom-40 right-10 text-[120px] font-black text-ethereal/10 rotate-12 animate-bounce font-impact uppercase tracking-tighter">NO CAP</div>
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[200px] font-black text-violet/5 animate-vibrate font-impact">GYATT</div>
                    <div className="absolute inset-0 bg-gradient-to-tr from-violet/20 via-transparent to-ethereal/10 mix-blend-overlay animate-pulse" />
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
                        <Database size={18} strokeWidth={1} />
                        <span className="uppercase">{vibe === 'brainrot' ? "SKIBIDI::AURAMAX" : "Observation::Shared_Workbench"}</span>
                    </div>

                    <h1 className={`text-6xl md:text-9xl tracking-tight italic leading-[0.85] transition-all duration-500 ${vibe === 'brainrot' ? 'text-violet-neon scale-110 drop-shadow-[0_0_30px_rgba(139,92,246,0.8)]' : 'text-ethereal font-serif'}`}>
                        {vibe === 'brainrot' ? "BRAINROT" : "SHARED"}<br />
                        <span className={vibe === 'brainrot' ? 'text-ethereal animate-pulse' : 'text-violet opacity-60'}>
                            {vibe === 'brainrot' ? "MAXING" : "WORKBENCH"}
                        </span>
                    </h1>

                    <div className={`grid grid-cols-1 md:grid-cols-3 gap-12 pt-12 border-t transition-colors duration-1000 ${vibe === 'brainrot' ? 'border-violet/60' : 'border-violet/10'}`}>
                        <div className="space-y-4">
                            <span className="text-[10px] font-sans text-violet tracking-widest uppercase opacity-60">Inquiry</span>
                            <p className="text-lg text-ethereal/80 italic leading-relaxed">
                                {vibe === 'brainrot' ? "MOG THE STATELESS INTERFACES. WE BUILDIN' AUTHORITATIVE AURAS ONLY. 👹" : "Move beyond stateless chat interfaces by building a deterministic, epoch-authoritative runtime that governs LLM behavior."}
                            </p>
                        </div>
                        <div className="space-y-4">
                            <span className="text-[10px] font-sans text-violet tracking-widest uppercase opacity-60">State</span>
                            <div className="flex items-center gap-2">
                                <Activity className={vibe === 'brainrot' ? "text-violet-neon animate-vibrate" : "text-violet"} size={16} strokeWidth={1} />
                                <span className={`text-sm font-mono tracking-widest uppercase ${vibe === 'brainrot' ? 'text-ethereal' : 'text-violet'}`}>
                                    {vibe === 'brainrot' ? "SKIBIDI_LEVEL_10" : "Production_Ready"}
                                </span>
                            </div>
                        </div>
                        <div className="space-y-4">
                            <span className="text-[10px] font-sans text-violet tracking-widest uppercase opacity-60">Foundation</span>
                            <p className="text-sm text-ethereal/60 font-mono italic">
                                {vibe === 'brainrot' ? "BRAINROT // RIZZ // GYATT // L + RATIO" : "FastAPI // React // SSE // SQLite // JSONL Ledger"}
                            </p>
                        </div>
                    </div>
                </motion.div>

                {/* Vibe Check Interactive Toggle */}
                <section className={`glass-panel celestial-border p-8 space-y-8 transition-all duration-1000 ${vibe === 'brainrot' ? 'border-violet bg-slate/60 shadow-[0_0_100px_rgba(139,92,246,0.3)] ring-4 ring-violet/20 animate-vibrate-slow' : 'bg-slate/20'}`}>
                    <div className={`flex items-center justify-between border-b pb-4 transition-colors duration-1000 ${vibe === 'brainrot' ? 'border-violet' : 'border-ethereal/10'}`}>
                        <div className="flex items-center gap-3 text-[10px] font-sans tracking-[0.3em] uppercase text-ethereal/40">
                            <Monitor size={14} className="text-violet/60" strokeWidth={1} />
                            {vibe === 'brainrot' ? "AURAMAX_INTERPRETER" : "Signal_Interpretation"}
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

                    <div className="min-h-[160px] flex items-center justify-center text-center px-4 md:px-12">
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={vibe}
                                initial={{ opacity: 0, scale: 0.9, rotate: vibe === 'brainrot' ? -5 : 0 }}
                                animate={{ opacity: 1, scale: 1, rotate: 0 }}
                                exit={{ opacity: 0, scale: 1.1, rotate: vibe === 'brainrot' ? 5 : 0 }}
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
                            <div className="space-y-6">
                                <p className={`text-ethereal/70 text-xl italic leading-relaxed border-l border-violet/20 pl-8 ${vibe === 'brainrot' ? 'text-violet-neon border-violet-neon animate-pulse uppercase' : 'font-serif'}`}>
                                    {vibe === 'brainrot' ? brainrotContent.impulse : "Most AI chat systems conflate projection with authority. Shared_Workbench enforces a strict separation:"}
                                </p>
                                <ul className="list-none space-y-4 pl-12">
                                    {(vibe === 'brainrot' ? ["THE RUNTIME IS THE GYATT.", "THE MODEL IS A MID GLAZER.", "COMMIT OR GET RATIO'D."] : ["The runtime owns state.", "The model proposes intent.", "Nothing mutates without commit."]).map((item, i) => (
                                        <li key={i} className={`flex items-center gap-4 text-sm tracking-widest transition-transform hover:translate-x-2 ${vibe === 'brainrot' ? 'text-violet-neon font-black italic' : 'font-sans text-violet'}`}>
                                            <ChevronRight size={14} className={vibe === 'brainrot' ? "text-violet-neon animate-bounce" : "text-violet/40"} /> {item.toUpperCase()}
                                        </li>
                                    ))}
                                </ul>
                                <p className={`text-sm font-sans italic pl-8 ${vibe === 'brainrot' ? 'text-ethereal font-black animate-bounce' : 'text-violet/60'}`}>
                                    {vibe === 'brainrot' ? "ZERO Ls, ALL Ws. 👹" : "This eliminates hidden drift, tool hallucination, and silent memory corruption."}
                                </p>
                            </div>
                        </section>

                        <section className="space-y-8">
                            <h2 className={`text-5xl italic text-ethereal flex items-center gap-4 ${vibe === 'brainrot' ? 'text-violet-neon text-6xl' : 'font-serif'}`}>
                                <ShieldAlert size={32} className={vibe === 'brainrot' ? "text-violet-neon animate-vibrate" : "text-violet"} strokeWidth={1} />
                                {vibe === 'brainrot' ? "SKIBIDI STEPS" : "Technical Milestones"}
                            </h2>
                            <div className="space-y-1">
                                {milestones.map((m, i) => (
                                    <div key={i} className={`group p-8 border-b border-ethereal/5 hover:bg-violet/5 transition-all space-y-3 ${vibe === 'brainrot' ? 'bg-violet/10 border-violet/20' : ''}`}>
                                        <div className="flex items-center gap-4">
                                            <GitBranch size={14} className={vibe === 'brainrot' ? "text-violet-neon" : "text-violet/40 group-hover:text-violet transition-colors"} />
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

                    {/* Collaborative Surface & Conclusion */}
                    <div className="space-y-16">
                        <div className={`relative glass-panel celestial-border aspect-video group overflow-hidden glow-violet shadow-[0_0_50px_rgba(139,92,246,0.4)] ${vibe === 'brainrot' ? 'border-violet bg-violet/20 animate-vibrate' : 'bg-slate/20'}`}>
                            <img
                                src="/img/projects/shared_workbench/Screenshot from 2026-02-12 15-55-38.png"
                                alt="Shared Workbench Workspace"
                                className={`w-full h-full object-cover transition-transform duration-1000 ${vibe === 'brainrot' ? 'scale-150 grayscale-0 brightness-150 invert animate-vibrate' : 'opacity-60 grayscale group-hover:scale-105 group-hover:grayscale-0'}`}
                            />
                            {vibe === 'brainrot' ? (
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <div className="text-white font-black text-6xl rotate-45 border-4 border-white p-4 animate-bounce">MOGGED</div>
                                </div>
                            ) : (
                                <div className="absolute inset-0 bg-void/20 group-hover:opacity-0 transition-opacity" />
                            )}
                            <div className="absolute top-4 right-4 text-[9px] font-sans bg-void/80 px-3 py-1 tracking-widest text-violet/60">
                                {vibe === 'brainrot' ? "GYATT::ACTIVE" : "Runtime::Surface_Active"}
                            </div>
                            <div className={`absolute inset-0 h-[1px] top-0 animate-scan pointer-events-none ${vibe === 'brainrot' ? 'bg-white shadow-[0_0_20px_white]' : 'bg-violet/20'}`} />
                        </div>

                        <section className={`p-12 border-l space-y-8 glass-panel transition-all ${vibe === 'brainrot' ? 'bg-violet/20 border-violet-neon shadow-2xl' : 'bg-slate/10 border-violet/20'}`}>
                            <h3 className={`text-[10px] font-sans tracking-[0.5em] uppercase opacity-60 ${vibe === 'brainrot' ? 'text-violet-neon text-sm font-black' : 'text-violet'}`}>
                                {vibe === 'brainrot' ? "FANUM TAX PANEL" : "Collaborative Surface"}
                            </h3>
                            <div className="space-y-6">
                                {modules.map((mod, i) => (
                                    <div key={i} className={`space-y-1 border-l border-transparent hover:border-violet/20 pl-4 transition-all ${vibe === 'brainrot' ? 'hover:border-violet-neon' : ''}`}>
                                        <div className={`text-lg italic transition-all ${vibe === 'brainrot' ? 'text-violet-neon font-black text-2xl uppercase animate-pulse' : 'text-ethereal opacity-80 font-serif'}`}>{mod.name}</div>
                                        <div className={`text-sm font-sans lowercase tracking-tight ${vibe === 'brainrot' ? 'text-ethereal font-black uppercase' : 'text-ethereal/40'}`}>{mod.desc}</div>
                                    </div>
                                ))}
                            </div>
                        </section>

                        <section className={`p-12 border-l space-y-8 glass-panel transition-all ${vibe === 'brainrot' ? 'bg-violet/20 border-violet-neon shadow-2xl' : 'bg-slate/10 border-violet/20'}`}>
                            <h3 className={`text-[10px] font-sans tracking-[0.5em] uppercase opacity-60 ${vibe === 'brainrot' ? 'text-violet-neon text-sm font-black' : 'text-violet'}`}>
                                {vibe === 'brainrot' ? "SKIBIDI THOUGHTS" : "Reflections"}
                            </h3>
                            <div className="space-y-6">
                                <p className={`text-2xl italic leading-relaxed ${vibe === 'brainrot' ? 'text-violet-neon font-black uppercase' : 'text-ethereal font-serif'}`}>
                                    "{vibe === 'brainrot' ? brainrotContent.reflections : "Most AI products are selling you a really good imaginary friend; this one is selling you a courtroom with receipts."}"
                                </p>
                                <p className={`text-sm font-sans italic ${vibe === 'brainrot' ? 'text-ethereal font-black uppercase' : 'text-violet/40'}`}>
                                    {vibe === 'brainrot' ? brainrotContent.conclusion : "Shared Workbench isn't built for vibes. It's built for when the vibes collapse and you need to know exactly who did what."}
                                </p>
                            </div>
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

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {(vibe === 'brainrot' ? brainrotContent.registry : [
                            { src: 'Screenshot from 2026-02-12 09-16-26.png', label: 'Neural Link' },
                            { src: 'Screenshot from 2026-02-12 09-16-50.png', label: 'Runtime View' },
                            { src: 'Screenshot from 2026-02-12 09-17-13.png', label: 'Epoch Commit' },
                            { src: 'Screenshot from 2026-02-12 13-17-23.png', label: 'Memory Audit' },
                            { src: 'Screenshot from 2026-02-12 13-17-36.png', label: 'Cortex Identity' },
                            { src: 'Screenshot from 2026-02-12 13-20-11.png', label: 'JSONL Ledger' },
                            { src: 'Screenshot from 2026-02-12 13-20-33.png', label: 'SSE Stream' },
                            { src: 'Screenshot from 2026-02-12 17-08-35.png', label: 'Control Plane' }
                        ]).map((img, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.1 }}
                                className="space-y-6 group"
                            >
                                <div className={`aspect-square glass-panel celestial-border overflow-hidden bg-slate/20 relative ${vibe === 'brainrot' ? 'border-violet-neon border-4 animate-vibrate' : ''}`}>
                                    <img
                                        src={`/img/projects/shared_workbench/${img.src}`}
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
                            href="https://github.com/Bradsadevnow/the_bottom_floor_of_an_ikea_where_they_build_stuff_or_pick_up_parts/tree/main/ai_system"
                            target="_blank"
                            rel="noopener noreferrer"
                            className={`px-12 py-5 border text-xs group transition-all flex items-center justify-center gap-4 tracking-[0.3em] uppercase ${vibe === 'brainrot' ? 'bg-white text-violet-neon border-white font-black animate-bounce scale-125 shadow-2xl' : 'border-violet/40 text-violet font-sans hover:bg-violet hover:text-void'}`}
                        >
                            <Github size={18} strokeWidth={1} className="group-hover:scale-110 transition-transform" />
                            {vibe === 'brainrot' ? "GITHUB_MOGGING" : "Repos_Controller"}
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
