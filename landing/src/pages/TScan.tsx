import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Activity, Monitor, Zap, ShieldAlert, Cpu, ChevronRight, Github } from 'lucide-react';

export function TScan() {
    const [vibe, setVibe] = useState<'tech' | 'normal' | 'brainrot'>('tech');

    const vibeChecks = {
        tech: {
            title: "MECHANISTIC_AUDIT::LW_PROBE_V3",
            content: "Layer-wise residual stream attribution indicates high-variance logit entropy in the late-stage transformer block."
        },
        normal: {
            title: "RESEARCH_NOTE",
            content: "T-Scan intercepts the model's internal hidden states to detect the exact moment where reasoning diverges from factual grounding."
        },
        brainrot: {
            title: "VIBE_CHECK_FAILED",
            content: "THE MODEL IS STRAIGHT UP TWEAKING, KING. 💀 GHOST IN THE MACHINE HAVING A FULL-BLOWN MIDLIFE CRISIS. WE CAPTURING INTERNAL GYATT IN REAL-TIME. NO CAP. 👺🔥"
        }
    };

    const brainrotContent = {
        impulse: "MOST EVALS SIMP FOR THE FINAL OUTPUT LIKE IT'S THE WHOLE STORY. T-SCAN? WE STALK THE ENTIRE CHAOTIC JOURNEY. REAL-TIME ATTENTION HEAD VISUALS WHILE THEY BEEF OVER CONTRADICTIONS — WE CLOCK THE CRASH BEFORE THE MODEL EVEN FINISHES LYING TO YOU 😭💀",
        milestones: [
            { title: "SKIBIDI IMPLEMENTATION", description: "Straight cloned causal probing + activation patching to hunt down those sneaky semantic circuits in the transformer guts. Absolute Aura. 👹" },
            { title: "3D GYATT PROJECTION", description: "Custom Godot 4 beast that yeets high-dim hidden states into a flyable 3D graph. Zoom through the model's brain like a cursed VR horror game. 👺" },
            { title: "CAUSAL MOGGING", description: "Poke random latent dimensions and watch token probs freak out. Perturbation testing on demon time. 👹" },
            { title: "LOGIT LENS RIZZ", description: "Live logit lens spy cam catching semantic meltdowns early — probs going flat? We see it first. Lock in. 🦾" },
            { title: "TEMPORAL GYATT REWIND", description: "Rewind activations like a crime scene tape — trace the exact hallucination seed back to the guilty token. 👺" },
            { title: "BEEF ALERT SYSTEM", description: "Red flags pop when the model's logic chains start beefing internally. Drift incoming? We scream it. 👹" },
            { title: "ROGUISH DIAGNOSTICS", description: "Python hooks snatch and log internals. No black-box excuses, fully rogue diagnostic mode. W. 👹🔥" }
        ],
        drift: {
            title: "The Drift Horizon",
            content: "DRIFT HITS WHEN LOGIT VARIANCE BLASTS PAST SEMANTIC STABILITY. TRANSLATION: MODEL STARTS SIMPING FOR WHAT IT THINKS YOU WANNA HEAR AND FORGETS ITS OWN DAMN PROOF. L. 👹",
            citation: "T-Scan Whitepaper v0.4 (unmedicated edition)"
        },
        conclusion: "STABILITY AIN'T ZERO MESS-UPS. IT'S SEEING THE MESS COMING FROM ORBIT. T-SCAN FLIPS THE BLACK BOX INTO A STRAIGHT-UP GLASS HOUSE — STARE AT THE CRACKS, KING 👹",
        registry: [
            { title: "Semantic Vector Mogging", description: "Maps the high-dim chaos where reasoning paths fork, merge, or straight-up snap like twigs. 👹" },
            { title: "Contradiction Beefs", description: "Blinking red when the model's internal logic turns into a civil war. 👺" },
            { title: "Temporal Rewind Rizz", description: "Zooms to the exact cursed token where the hallucination virus first dropped. 🦾" }
        ]
    };

    const milestones = vibe === 'brainrot' ? brainrotContent.milestones : [
        {
            title: "INDEPENDENT IMPLEMENTATION",
            description: "Successfully reproduced causal probing and activation patching workflows to isolate specific semantic circuits within the transformer architecture."
        },
        {
            title: "3D LATENT SPACE PROJECTION",
            description: "Engineered a custom Godot 4 visualization engine to project high-dimensional hidden states into a navigable 3D graph."
        },
        {
            title: "CAUSAL SCRUBBING",
            description: "Conducted perturbation tests by 'poking' specific dimensions in the latent space and observing the effects on token probability."
        },
        {
            title: "LOGIT LENS INTEGRATION",
            description: "Developed real-time logit lens to observe token probability distributions and identify early signs of semantic instability."
        },
        {
            title: "TEMPORAL REWIND CAPABILITY",
            description: "Implemented a system to trace back the exact sequence of activations leading to a detected hallucination or contradiction."
        },
        {
            title: "CONTRADICTION ALERT SYSTEM",
            description: "Engineered a protocol to flag internal inconsistencies within the model's reasoning pathways, indicating potential drift."
        },
        {
            title: "STANDALONE DIAGNOSTIC SUITE",
            description: "Developed as a standalone diagnostic suite using Python-based hooks to intercept and log internal model activations."
        }
    ];

    return (
        <main className={`pt-32 pb-24 px-8 relative overflow-hidden transition-all duration-300 ${vibe === 'brainrot' ? 'bg-violet/20 animate-vibrate-slow' : 'bg-void'}`}>
            {vibe === 'brainrot' && (
                <div className="fixed inset-0 pointer-events-none z-[100] overflow-hidden">
                    <div className="absolute top-20 left-10 text-[80px] font-black text-violet/20 -rotate-12 animate-pulse font-impact">MOGGED</div>
                    <div className="absolute bottom-40 right-10 text-[120px] font-black text-ethereal/10 rotate-12 animate-bounce font-impact uppercase tracking-tighter">THE CIRCUIT</div>
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[200px] font-black text-violet/5 animate-vibrate font-impact">SKIBIDI</div>
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
                        <Search size={18} strokeWidth={1} />
                        <span className="uppercase">{vibe === 'brainrot' ? "SKIBIDI::SCAN" : "Research::T-Scan"}</span>
                    </div>

                    <h1 className={`text-7xl md:text-9xl tracking-tight italic leading-[0.85] transition-all duration-500 ${vibe === 'brainrot' ? 'text-violet-neon scale-110 drop-shadow-[0_0_30px_rgba(139,92,246,0.8)]' : 'text-ethereal font-serif'}`}>
                        {vibe === 'brainrot' ? "SKIBIDI" : "T-SCAN"}<br />
                        <span className={vibe === 'brainrot' ? 'text-ethereal animate-pulse' : 'text-violet opacity-60'}>
                            {vibe === 'brainrot' ? "MOGGING" : "PROTOCOL"}
                        </span>
                    </h1>

                    <div className={`grid grid-cols-1 md:grid-cols-3 gap-12 pt-12 border-t transition-colors duration-1000 ${vibe === 'brainrot' ? 'border-violet/60' : 'border-violet/10'}`}>
                        <div className="space-y-4">
                            <span className="text-[10px] font-sans text-violet tracking-widest uppercase opacity-60">Inquiry</span>
                            <p className="text-lg text-ethereal/80 italic leading-relaxed">
                                {vibe === 'brainrot'
                                    ? "STALKING THE MODEL'S INTERNAL CHAOS BEFORE IT LIES TO YOUR FACE. 👹"
                                    : "A framework for scanning the temporal logic of LLMs, identifying where reasoning drifts into hallucination."}
                            </p>
                        </div>
                        <div className="space-y-4">
                            <span className="text-[10px] font-sans text-violet tracking-widest uppercase opacity-60">State</span>
                            <div className="flex items-center gap-2">
                                <Activity className={vibe === 'brainrot' ? "text-violet-neon animate-vibrate" : "text-violet"} size={16} strokeWidth={1} />
                                <span className={`text-sm font-mono tracking-widest uppercase ${vibe === 'brainrot' ? 'text-ethereal' : 'text-violet'}`}>
                                    {vibe === 'brainrot' ? "SKIBIDI_ALPHA" : "Internal_Alpha"}
                                </span>
                            </div>
                        </div>
                        <div className="space-y-4">
                            <span className="text-[10px] font-sans text-violet tracking-widest uppercase opacity-60">Foundation</span>
                            <p className="text-sm text-ethereal/60 font-mono italic">
                                {vibe === 'brainrot' ? "TRANSFORMERS // RIZZ // LOGITS // GYATT" : "Transformer Analysis // Temporal Logics // Logit Lenses"}
                            </p>
                        </div>
                    </div>
                </motion.div>

                {/* Vibe Check Interactive Toggle */}
                <section className={`glass-panel celestial-border p-8 space-y-8 transition-all duration-1000 ${vibe === 'brainrot' ? 'border-violet bg-slate/60 shadow-[0_0_100px_rgba(139,92,246,0.3)] ring-4 ring-violet/20' : 'bg-slate/20'}`}>
                    <div className={`flex items-center justify-between border-b pb-4 transition-colors duration-1000 ${vibe === 'brainrot' ? 'border-violet' : 'border-ethereal/10'}`}>
                        <div className="flex items-center gap-3 text-[10px] font-sans tracking-[0.3em] uppercase text-ethereal/40">
                            <Monitor size={14} className="text-violet/60" strokeWidth={1} />
                            {vibe === 'brainrot' ? "BRAIN_ROT_MONITOR" : "Signal_Interpretation"}
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
                            <div className="space-y-8">
                                <p className={`text-ethereal/70 text-xl italic leading-relaxed border-l border-violet/20 pl-8 ${vibe === 'brainrot' ? 'text-violet-neon border-violet-neon animate-pulse uppercase' : 'font-serif'}`}>
                                    {vibe === 'brainrot' ? brainrotContent.impulse : (
                                        "Most model evaluations look at final outputs. T-Scan looks at the journey. By visualizing the attention heads in real-time as they resolve contradictions, we can predict a failure state before the model even finishes its sentence."
                                    )}
                                </p>
                                <div className={`glass-panel celestial-border p-2 transition-all ${vibe === 'brainrot' ? 'border-violet-neon bg-violet/20 shadow-[0_0_30px_rgba(139,92,246,0.5)]' : 'bg-slate/20'}`}>
                                    <img
                                        src="/img/projects/t-scan/001_per-token_mri.png"
                                        alt="Per-token MRI Scan"
                                        className={`w-full opacity-80 hover:opacity-100 transition-opacity ${vibe === 'brainrot' ? 'animate-pulse contrast-125' : ''}`}
                                    />
                                    <div className={`p-4 text-[10px] font-sans tracking-widest uppercase ${vibe === 'brainrot' ? 'text-violet-neon font-black' : 'text-violet/60'}`}>
                                        {vibe === 'brainrot' ? "SKIBIDI_SCAN::TRANSFORMER_GUT_CHECK" : "Scan_Identity::MRI_001_TRANSFORMER_RESIDUAL"}
                                    </div>
                                </div>
                            </div>
                        </section>

                        <section className="space-y-8">
                            <h2 className={`text-5xl italic text-ethereal flex items-center gap-4 ${vibe === 'brainrot' ? 'text-violet-neon text-6xl' : 'font-serif'}`}>
                                <ShieldAlert size={32} className={vibe === 'brainrot' ? "text-violet-neon animate-vibrate" : "text-violet"} strokeWidth={1} />
                                {vibe === 'brainrot' ? "SKIBIDI STEPS" : "Protocol Milestones"}
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
                        <section className={`p-12 border-l space-y-8 glass-panel transition-all ${vibe === 'brainrot' ? 'bg-violet/20 border-violet-neon shadow-2xl animate-pulse' : 'bg-slate/10 border-violet/20 glow-violet relative overflow-hidden'}`}>
                            <div className={`absolute inset-0 pointer-events-none ${vibe === 'brainrot' ? 'bg-violet/10 animate-scan' : 'bg-violet/5 animate-pulse'}`} />
                            <h3 className={`text-[10px] font-sans tracking-[0.5em] uppercase opacity-60 ${vibe === 'brainrot' ? 'text-violet-neon text-sm font-black' : 'text-violet'}`}>
                                {vibe === 'brainrot' ? brainrotContent.drift.title : "The Drift Horizon"}
                            </h3>
                            <p className={`text-xl italic leading-relaxed relative z-10 ${vibe === 'brainrot' ? 'text-violet-neon font-black uppercase' : 'text-ethereal/80 font-serif'}`}>
                                "{vibe === 'brainrot' ? brainrotContent.drift.content : (
                                    "Drift occurs when the internal logit variance exceeds the threshold of semantic stability. In simpler terms: the model starts guessing what it thinks you want to hear, and forgets what it was actually trying to prove."
                                )}"
                                <span className={`block text-[10px] font-sans mt-4 opacity-40 ${vibe === 'brainrot' ? 'text-ethereal' : 'text-violet/60'}`}>
                                    — {vibe === 'brainrot' ? brainrotContent.drift.citation : "T-SCAN Whitepaper v0.4"}
                                </span>
                            </p>
                        </section>

                        <section className={`p-12 border-l space-y-8 glass-panel transition-all ${vibe === 'brainrot' ? 'bg-slate/60 border-violet-neon shadow-2xl animate-vibrate-slow' : 'bg-slate/10 border-violet/20'}`}>
                            <h3 className={`text-[10px] font-sans tracking-[0.5em] uppercase opacity-60 ${vibe === 'brainrot' ? 'text-violet-neon text-sm font-black' : 'text-violet'}`}>
                                {vibe === 'brainrot' ? "SKIBIDI THOUGHTS" : "Conclusion"}
                            </h3>
                            <p className={`text-2xl italic leading-relaxed ${vibe === 'brainrot' ? 'text-violet-neon font-black uppercase' : 'text-ethereal font-serif'}`}>
                                "{vibe === 'brainrot' ? brainrotContent.conclusion : (
                                    "Stability is not the absence of error, but the ability to observe it. T-Scan is the lens that turns the black box into a glass house."
                                )}"
                            </p>
                        </section>
                    </div>
                </div>

                {/* Technical Registry */}
                <section className="space-y-12">
                    <div className="flex items-center gap-4">
                        <Cpu className={vibe === 'brainrot' ? "text-violet-neon animate-vibrate" : "text-violet"} size={32} strokeWidth={1} />
                        <h2 className={`text-5xl italic tracking-tight uppercase ${vibe === 'brainrot' ? 'text-violet-neon font-black text-6xl' : 'text-ethereal font-serif'}`}>
                            {vibe === 'brainrot' ? "THE VAULT" : "Registry"}
                        </h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 text-center">
                        {(vibe === 'brainrot' ? brainrotContent.registry : [
                            { title: "Semantic Vector Mapping", description: "Visualizing the high-dimensional space where reasoning paths branch and merge.", img: "003_circuit_01.png" },
                            { title: "Contradiction Alerts", description: "Real-time indicators when internal logic chains become mutually exclusive.", img: "004_circuit_02.png" },
                            { title: "Temporal Rewind", description: "Analyzing the exact token where the first seed of hallucination was planted.", img: "005_circuit_03.png" }
                        ]).map((module, i) => (
                            <div key={i} className={`p-8 glass-panel celestial-border space-y-6 group transition-all ${vibe === 'brainrot' ? 'border-violet-neon bg-violet/20 shadow-xl' : 'bg-slate/10'}`}>
                                <div className={`text-[9px] font-sans tracking-[0.3em] uppercase ${vibe === 'brainrot' ? 'text-violet-neon font-black' : 'text-violet/60'}`}>Module::0{i + 1}</div>
                                <div className="aspect-video bg-void/40 overflow-hidden mb-6">
                                    <img
                                        src={`/img/projects/t-scan/${(module as any).img || '002_early_circuits.png'}`}
                                        alt={module.title}
                                        className={`w-full h-full object-cover transition-all duration-700 ${vibe === 'brainrot' ? 'opacity-100 grayscale-0 contrast-125 group-hover:scale-110' : 'opacity-60 group-hover:opacity-100 group-hover:scale-105'}`}
                                    />
                                </div>
                                <h4 className={`text-2xl italic transition-colors ${vibe === 'brainrot' ? 'text-violet-neon font-black uppercase' : 'text-ethereal group-hover:text-violet font-serif'}`}>{module.title}</h4>
                                <p className={`text-sm leading-relaxed ${vibe === 'brainrot' ? 'text-white font-black uppercase' : 'text-ethereal/40 font-sans'}`}>
                                    {module.description}
                                </p>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Visual Evidence Gallery */}
                <section className="space-y-12">
                    <div className="flex items-center gap-4">
                        <Monitor className={vibe === 'brainrot' ? "text-violet-neon animate-vibrate" : "text-violet"} size={32} strokeWidth={1} />
                        <h2 className={`text-5xl italic tracking-tight uppercase ${vibe === 'brainrot' ? 'text-violet-neon font-black text-6xl' : 'text-ethereal font-serif'}`}>
                            {vibe === 'brainrot' ? "SKIBIDI EVIDENCE" : "Visual Evidence"}
                        </h2>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        {[
                            "Screenshot from 2026-01-05 10-35-38.png",
                            "Screenshot from 2026-01-05 10-38-08.png",
                            "Screenshot from 2026-01-05 10-38-48.png",
                            "Screenshot from 2026-01-05 11-20-49.png"
                        ].map((img, i) => (
                            <div key={i} className={`glass-panel celestial-border p-2 group overflow-hidden transition-all ${vibe === 'brainrot' ? 'border-violet-neon bg-violet/20 hover:shadow-[0_0_50px_rgba(139,92,246,0.6)]' : 'bg-slate/5'}`}>
                                <img
                                    src={`/img/projects/t-scan/${img}`}
                                    alt={`Research Screenshot ${i + 1}`}
                                    className={`w-full transition-all duration-500 ${vibe === 'brainrot' ? 'opacity-100 contrast-125' : 'opacity-60 hover:opacity-100'}`}
                                />
                                <div className={`p-4 flex justify-between items-center text-[9px] font-sans tracking-[0.2em] uppercase ${vibe === 'brainrot' ? 'text-violet-neon font-black' : 'text-violet/40'}`}>
                                    <span>Capture::Node_{i + 1}</span>
                                    <span>{vibe === 'brainrot' ? "MOG_AUDIT_LOGS" : "Alpha_Audit_Logs"}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Call to Action */}
                <motion.div
                    whileInView={{ opacity: 1 }}
                    initial={{ opacity: 0 }}
                    className={`p-16 text-center space-y-12 transition-all ${vibe === 'brainrot' ? 'border-violet-neon bg-violet/40 scale-105 shadow-[0_0_150px_rgba(139,92,246,0.6)]' : 'border border-violet/10 bg-void/20'}`}
                >
                    <h3 className={`text-4xl italic tracking-wide uppercase ${vibe === 'brainrot' ? 'text-white font-black text-6xl drop-shadow-xl animate-vibrate' : 'text-ethereal font-serif'}`}>
                        {vibe === 'brainrot' ? "JOIN THE CIRCLE 👹" : "Audit the Continuity"}
                    </h3>
                    <div className="flex justify-center flex-col items-center gap-8">
                        <a
                            href="https://github.com/Bradsadevnow/t-scan"
                            target="_blank"
                            rel="noopener noreferrer"
                            className={`px-12 py-5 border text-xs group transition-all flex items-center justify-center gap-4 tracking-[0.3em] uppercase ${vibe === 'brainrot' ? 'bg-white text-violet-neon border-white font-black animate-bounce scale-125 shadow-2xl' : 'border-violet/40 text-ethereal/80 font-mono hover:bg-violet/10'}`}
                        >
                            <Github size={18} strokeWidth={1} className="group-hover:scale-110 transition-transform" />
                            {vibe === 'brainrot' ? "GITHUB_MOGGING" : "REPOS_RESEARCH"}
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
