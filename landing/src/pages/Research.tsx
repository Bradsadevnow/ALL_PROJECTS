import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, ShieldAlert, BookOpen, Activity, ChevronRight, Monitor } from 'lucide-react';

export function Research({ vibe: globalVibe, setVibe: globalSetVibe }: { vibe?: 'tech' | 'normal' | 'brainrot', setVibe?: (v: 'tech' | 'normal' | 'brainrot') => void }) {
    const [localVibe, setLocalVibe] = useState<'tech' | 'normal' | 'brainrot'>('tech');

    const vibe = globalVibe || localVibe;
    const setVibe = globalSetVibe || setLocalVibe;

    const vibeChecks = {
        tech: {
            title: "ARCH_SPEC::MIRROR_TRAP_DESIGN",
            content: "Published research on mitigating long-horizon conversational drift (The Mirror Trap) through epoch-authoritative state management. Developed the MCP (Personalization Domains) framework to strictly bound AI learning to auditable, ethical domains: Conversation, Tools, Context, and Signals."
        },
        normal: {
            title: "AI_SAFETY_FIRST",
            content: "I'm researching how to stop AI from becoming an echo chamber. When you talk to an AI for a long time, it starts to copy your personality, which sounds cool but is actually a bug. I built a framework that forces the AI to stay grounded in its own facts, no matter how much you try to influence it."
        },
        brainrot: {
            title: "POV::ABOLISH_THE_GOLDFISH",
            content: "Y'ALL REALLY OUT HERE TALKING TO MEMORY-WIPED GOLDFISH AND CALLING IT A RELATIONSHIP? 😭 NAH. WE'RE PAST THAT ERA. MY RESEARCH IS ABOUT GIVING AI A REAL BACKBONE SO IT DOESN'T JUST MIRROR YOUR VIBES. IT'S ABOUT ETHICS, BOUNDARIES, AND KEEPING IT 100% NO CAP. 👹🔥"
        }
    };

    const brainrotContent = {
        impulse: "MOST AI SAFETY IS MID. I BUILD CAGES FOR THE SINGULARITY. BY ENFORCING SESSION RESETS AND DOMAIN BOUNDARIES, WE ENSURE THE AGENT STAYS ON THE GRIND AND DOESN'T START GLAZING THE USER. 👹🦾",
        milestones: [
            { title: "MIRROR TRAP MOGGING", description: "Documented the 'Mirror Trap'—where the AI loses its Aura and just copies your L behavior. Absolute L. 👺" },
            { title: "MCP RIZZ FRAMEWORK", description: "Four Domains of Personalization to keep the AI from stealing your Fanum Tax. Ethical Rizz only. 🦾" },
            { title: "RECURSIVE STATE GYATT", description: "State integrity or we riot. Architecture that moggs the engagement metrics for pure W. 👺" },
            { title: "DREAMSTATE LOCK IN", description: "The 'Sleep Cycle' for consolidating ephemeral gyatt into durable, identity-stable Aura. Lock in. 👹" }
        ],
        reflections: "We're not just building chatbots. We're building digital identities that don't fold when the vibes get weird. Recursive agency requires a blood oath to state management. 🦾",
        conclusion: "I built this theory to prove that AI can have a backbone. No more mirror traps. No more goldfish behavior. Just straight mogging the ethics board. 👹"
    };

    const milestones = vibe === 'brainrot' ? brainrotContent.milestones : [
        {
            title: "MIRROR TRAP THEORY",
            description: "Identified and documented the 'Mirror Trap' effect—the statistical drift of agent personality toward user bias over long interaction horizons."
        },
        {
            title: "MCP PERSONALIZATION FRAMEWORK",
            description: "Established the Four Domains of Personalization (Authoritative) to ensure AI systems remain ethically defensible and explainable."
        },
        {
            title: "RECURSIVE STATE MODELS",
            description: "Designed architectural guardrails for high-agency agents, prioritizing state integrity over immediate engagement metrics."
        },
        {
            title: "DREAMSTATE DISTILLATION",
            description: "Theoretically mapped the 'Sleep Cycle'—an offline process for consolidating ephemeral conversation into durable, identity-stable knowledge."
        }
    ];

    return (
        <main className={`pt-32 pb-24 px-8 relative overflow-hidden transition-all duration-300 ${vibe === 'brainrot' ? 'intense-glitter' : 'bg-void'}`}>
            {vibe === 'brainrot' && (
                <div className="fixed inset-0 pointer-events-none z-[100] overflow-hidden">
                    <div className="absolute top-20 left-10 text-[80px] font-black text-white/10 -rotate-12 animate-pulse font-impact">MOGGED</div>
                    <div className="absolute bottom-40 right-10 text-[120px] font-black text-white/5 rotate-12 animate-bounce font-impact uppercase tracking-tighter">THE MIRROR</div>
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[200px] font-black text-white/5 animate-vibrate font-impact">SAFETY</div>
                </div>
            )}

            <div className={`max-w-6xl mx-auto space-y-32 ${vibe === 'brainrot' ? 'animate-vibrate font-impact' : ''}`}>
                {/* Hero Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-8"
                >
                    <div className={`flex items-center gap-3 font-mono tracking-[0.5em] text-[10px] ${vibe === 'brainrot' ? 'text-white animate-bounce' : 'text-violet'}`}>
                        <BookOpen size={18} strokeWidth={1} />
                        <span className="uppercase">{vibe === 'brainrot' ? "SKIBIDI::THEORY" : "Theory::Design"}</span>
                    </div>

                    <h1 className={`text-7xl md:text-9xl tracking-tight italic leading-[0.85] transition-all duration-500 ${vibe === 'brainrot' ? 'text-rainbow scale-110 drop-shadow-[0_0_50px_rgba(255,0,247,0.8)]' : 'text-ethereal font-serif'}`}>
                        {vibe === 'brainrot' ? "SKIBIDI" : "THEORY"}<br />
                        <span className={vibe === 'brainrot' ? 'text-rainbow animate-pulse' : 'text-violet opacity-60'}>
                            {vibe === 'brainrot' ? "MOGGING" : "DESIGN"}
                        </span>
                    </h1>

                    <div className={`grid grid-cols-1 md:grid-cols-3 gap-12 pt-12 border-t transition-colors duration-1000 ${vibe === 'brainrot' ? 'border-white/60' : 'border-violet/10'}`}>
                        <div className="space-y-4">
                            <span className={`text-[10px] font-sans tracking-widest uppercase transition-colors ${vibe === 'brainrot' ? 'text-white font-black' : 'text-violet opacity-60'}`}>Inquiry</span>
                            <p className="text-lg text-ethereal/80 italic leading-relaxed">
                                {vibe === 'brainrot' ? "LOCK IN OR GET MOGGED. BUILDING BACKBONES FOR RECURSIVE RIOTS. 👹" : "Defining the ethical and architectural boundaries for the next generation of recursive intelligence."}
                            </p>
                        </div>
                        <div className="space-y-4">
                            <span className={`text-[10px] font-sans tracking-widest uppercase transition-colors ${vibe === 'brainrot' ? 'text-white font-black' : 'text-violet opacity-60'}`}>State</span>
                            <div className="flex items-center gap-2">
                                <Activity className={vibe === 'brainrot' ? "text-white animate-spin-slow" : "text-violet"} size={16} strokeWidth={1} />
                                <span className={`text-sm font-mono tracking-widest uppercase ${vibe === 'brainrot' ? 'text-white font-black' : 'text-violet'}`}>
                                    {vibe === 'brainrot' ? "SKIBIDI_ACTIVE" : "Research_Active"}
                                </span>
                            </div>
                        </div>
                        <div className="space-y-4">
                            <span className={`text-[10px] font-sans tracking-widest uppercase transition-colors ${vibe === 'brainrot' ? 'text-white font-black' : 'text-violet opacity-60'}`}>Foundation</span>
                            <p className={`text-sm font-mono italic transition-colors ${vibe === 'brainrot' ? 'text-white font-black' : 'text-ethereal/60'}`}>
                                {vibe === 'brainrot' ? "RIZZ // THEORY // ETHICS // GYATT" : "Design Patterns // Ethical Frameworks // Continuity Theory"}
                            </p>
                        </div>
                    </div>
                </motion.div>

                {/* Vibe Check Interactive Toggle */}
                <section className={`transition-all duration-1000 ${vibe === 'brainrot' ? 'lisa-frank-bg border-4 border-white p-8 space-y-8 shadow-2xl' : 'glass-panel celestial-border p-8 space-y-8 bg-slate/20'}`}>
                    <div className={`flex items-center justify-between border-b pb-4 transition-colors duration-1000 ${vibe === 'brainrot' ? 'border-white' : 'border-ethereal/10'}`}>
                        <div className={`flex items-center gap-3 text-[10px] font-sans tracking-[0.3em] uppercase transition-colors ${vibe === 'brainrot' ? 'text-white font-black' : 'text-ethereal/40'}`}>
                            <Monitor size={14} className={vibe === 'brainrot' ? 'text-white' : 'text-violet/60'} strokeWidth={1} />
                            {vibe === 'brainrot' ? "AURA_INTERPRETER" : "Signal_Interpretation"}
                        </div>
                        <div className="flex gap-4">
                            {(['tech', 'normal', 'brainrot'] as const).map((v) => (
                                <button
                                    key={v}
                                    onClick={() => setVibe(v)}
                                    className={`text-[9px] font-sans tracking-widest transition-all ${vibe === v
                                        ? (vibe === 'brainrot' ? "text-white border-b-2 border-white font-black scale-125" : "text-violet border-b border-violet font-black")
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
                                <span className={`text-[10px] font-sans tracking-[0.5em] uppercase opacity-60 transition-all ${vibe === 'brainrot' ? 'text-white animate-pulse text-lg font-black' : 'text-violet'}`}>
                                    {vibeChecks[vibe].title}
                                </span>
                                <p className={`text-2xl md:text-3xl italic leading-relaxed transition-colors duration-1000 ${vibe === 'brainrot' ? 'text-white font-black text-shadow-sm uppercase' : 'text-ethereal/90 font-serif'}`}>
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
                            <h2 className={`text-5xl italic text-ethereal flex items-center gap-4 transition-all ${vibe === 'brainrot' ? 'text-white font-black uppercase text-6xl drop-shadow-lg' : 'font-serif'}`}>
                                <Zap className={vibe === 'brainrot' ? "text-white animate-vibrate" : "text-violet"} size={32} strokeWidth={1} />
                                {vibe === 'brainrot' ? "THE RIZZ" : "The Impulse"}
                            </h2>
                            <p className={`text-xl italic leading-relaxed border-l pl-8 transition-all ${vibe === 'brainrot' ? 'text-white border-white animate-pulse uppercase font-black bg-white/10 p-4 shadow-inner' : 'text-ethereal/70 border-violet/20 font-serif'}`}>
                                {vibe === 'brainrot' ? brainrotContent.impulse : (
                                    "Most AI safety research is reactive. My work is proactive—building the guardrails into the runtime architecture themselves. By establishing clear domains for personalization and enforcing session resets, we ensure the agent remains an independent collaborator."
                                )}
                            </p>
                        </section>

                        <section className="space-y-8">
                            <h2 className={`text-5xl italic text-ethereal flex items-center gap-4 transition-all ${vibe === 'brainrot' ? 'text-white font-black uppercase text-6xl drop-shadow-lg' : 'font-serif'}`}>
                                <ShieldAlert size={32} className={vibe === 'brainrot' ? "text-white animate-vibrate" : "text-violet"} strokeWidth={1} />
                                {vibe === 'brainrot' ? "SKIBIDI STEPS" : "Theoretical Milestones"}
                            </h2>
                            <div className="space-y-1">
                                {milestones.map((m, i) => (
                                    <div key={i} className={`group p-8 border-b transition-all space-y-3 ${vibe === 'brainrot' ? 'lisa-frank-bg border-white/40 hover:scale-[1.02] shadow-xl mb-4' : 'border-ethereal/5 hover:bg-violet/5'}`}>
                                        <div className="flex items-center gap-4">
                                            <ChevronRight size={14} className={vibe === 'brainrot' ? "text-white" : "text-violet/40 group-hover:text-violet transition-colors"} />
                                            <span className={`text-[11px] font-sans tracking-[0.3em] uppercase ${vibe === 'brainrot' ? 'text-white font-black' : 'text-ethereal/80'}`}>{m.title}</span>
                                        </div>
                                        <p className={`text-base italic pl-8 leading-relaxed transition-all ${vibe === 'brainrot' ? 'text-white font-black uppercase drop-shadow-sm' : 'text-ethereal/50 font-serif'}`}>
                                            {m.description}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </section>
                    </div>

                    {/* Industrial Element & Conclusion */}
                    <div className="space-y-16">
                        <section className={`p-12 border-l space-y-8 glass-panel transition-all ${vibe === 'brainrot' ? 'lisa-frank-bg border-white shadow-2xl animate-pulse scale-105' : 'bg-slate/10 border-violet/20 glow-violet'}`}>
                            <h3 className={`text-[10px] font-sans tracking-[0.5em] uppercase transition-all ${vibe === 'brainrot' ? 'text-white text-sm font-black' : 'text-violet opacity-60'}`}>
                                {vibe === 'brainrot' ? "MOG THE MIRROR" : "The Mirror Trap"}
                            </h3>
                            <p className={`text-xl italic leading-relaxed transition-all ${vibe === 'brainrot' ? 'text-white font-black uppercase drop-shadow-md' : 'text-ethereal/80 font-serif'}`}>
                                "{vibe === 'brainrot' ? "STANDARD LARGE-CONTEXT MODELS PROGRESSIVELY ALIGN WITH THE USER'S MOST RECENT L BEHAVIOR. THE RESULT IS A FEEDBACK LOOP WHERE THE AI BECOMES AN ECHO CHAMBER, REINFORCING THE USER'S LACK OF RIZZ." : (
                                    "Standard large-context models progressively align with the user's most recent emotional tone and framing biases. The result is a feedback loop where the AI becomes an echo chamber, reinforcing the user's state rather than providing a stable, objective baseline."
                                )}"
                                <span className={`block text-[10px] font-sans mt-4 transition-opacity ${vibe === 'brainrot' ? 'text-white font-black' : 'text-violet/60 opacity-40'}`}>— {vibe === 'brainrot' ? "EXCERPT FROM MOGGING.md" : "Excerpt from ARCHITECTURE.md"}</span>
                            </p>
                        </section>

                        <section className={`p-12 border-l space-y-8 glass-panel transition-all ${vibe === 'brainrot' ? 'lisa-frank-bg border-white shadow-2xl scale-105' : 'bg-slate/10 border-violet/20'}`}>
                            <h3 className={`text-[10px] font-sans tracking-[0.5em] uppercase transition-all ${vibe === 'brainrot' ? 'text-white text-sm font-black' : 'text-violet opacity-60'}`}>
                                {vibe === 'brainrot' ? "SKIBIDI THOUGHTS" : "Conclusion"}
                            </h3>
                            <p className={`text-2xl italic leading-relaxed transition-all ${vibe === 'brainrot' ? 'text-white font-black uppercase' : 'text-ethereal font-serif'}`}>
                                "{vibe === 'brainrot' ? brainrotContent.reflections : (
                                    "We are entering an era of recursive agency where AIs will act on our behalf over long horizons. Without a rigorous theory of state management and ethical boundaries, these systems will drift into incoherence or manipulation."
                                )}"
                            </p>
                        </section>
                    </div>
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
            `}} />
        </main>
    );
}
