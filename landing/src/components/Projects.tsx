import { motion } from 'framer-motion';
import { LayoutGrid } from 'lucide-react';
import { Link } from 'react-router-dom';

export function Projects({ vibe }: { vibe: 'tech' | 'normal' | 'brainrot' }) {
    return (
        <section id="projects" className={`py-32 px-8 relative overflow-hidden transition-all duration-500 ${vibe === 'brainrot' ? 'bg-violet/10' : ''}`}>
            <div className="max-w-6xl mx-auto space-y-24">
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.8 }}
                    viewport={{ once: true }}
                    className={`flex flex-col md:flex-row items-end justify-between gap-8 border-b pb-12 transition-colors ${vibe === 'brainrot' ? 'border-violet-neon' : 'border-violet/20'}`}
                >
                    <div className="space-y-4">
                        <div className={`flex items-center gap-3 font-black tracking-[0.5em] text-xs transition-colors ${vibe === 'brainrot' ? 'text-white animate-bounce' : 'text-violet'}`}>
                            <LayoutGrid size={18} />
                            <span className="uppercase">{vibe === 'brainrot' ? "MOG_LOGS::BRAINROT" : "Portfolio::Registry"}</span>
                        </div>
                        <h2 className={`text-6xl md:text-8xl font-black tracking-tighter transition-all ${vibe === 'brainrot' ? 'text-rainbow scale-110 drop-shadow-[0_0_30px_rgba(255,0,247,0.5)]' : 'glitch-effect'}`}>
                            {vibe === 'brainrot' ? "SKIBIDI" : "PROJ"}<span className={vibe === 'brainrot' ? 'text-white' : 'text-violet'}>{vibe === 'brainrot' ? "_WINS" : "ECTS"}</span>
                        </h2>
                    </div>

                    <p className={`max-w-md font-mono text-sm leading-relaxed tracking-tighter transition-all ${vibe === 'brainrot' ? 'text-white font-black uppercase text-lg animate-vibrate-slow' : 'text-ethereal/60'}`}>
                        {vibe === 'brainrot'
                            ? "WE ONLY SHIP ABSOLUTE WINS. 👹 IF IT DOESN'T MOG THE OPPS, IT'S NOT IN THE REGISTRY. LOCK IN OR GET LEFT. 👺🔥"
                            : "Explorations in recursive intelligence, industrial structuralism, and continuity-first application design. Each entry represents a distinct node in the developmental loop."
                        }
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12">
                    {[
                        { to: "/projects/t-scan", num: "01", title: vibe === 'brainrot' ? "SKIBIDI_SCAN" : "T-Scan", desc: vibe === 'brainrot' ? "MOGGING THE TRANSFORMERS. 👹" : "Mechanistic interpretability mapping on Llama 3.2 3B.", tag: vibe === 'brainrot' ? "GYATT_RESEARCH" : "Research Component" },
                        { to: "/projects/shared-workbench", num: "02", title: vibe === 'brainrot' ? "RIZZ_BENCH" : "Workbench", desc: vibe === 'brainrot' ? "CRACKED RUNTIME FOR THE GOATS. 👺" : "A state-authoritative runtime for LLM collaboration.", tag: vibe === 'brainrot' ? "AURA_CORE" : "Infrastructure" },
                        { to: "/projects/bob", num: "03", title: vibe === 'brainrot' ? "BOB_THE_MOGGER" : "Bob", desc: vibe === 'brainrot' ? "ZERO ILLEGAL MOVES OR WE RIOT. 👹" : "Zero-hallucination MTG AI with a deterministic rules engine and schema-constrained LLM strategy.", tag: vibe === 'brainrot' ? "EDGE_LORD" : "Constraint Engine" },
                        { to: "/projects/halcyon", num: "04", title: vibe === 'brainrot' ? "HALCYON_GYATT" : "Halcyon", desc: vibe === 'brainrot' ? "DUAL VECTOR EMOTIONAL GYATT MEMORY. 👺" : "Persistent AI agent with dual-vector emotional memory — content and affective embeddings via Qdrant.", tag: vibe === 'brainrot' ? "RIZZ_LOGIC" : "Emotive Memory" },
                        { to: "/projects/iris", num: "05", title: vibe === 'brainrot' ? "IRIS_MAXING" : "Iris", desc: vibe === 'brainrot' ? "RECURSIVE SOUL ENGINE LOCKING IN. 👹" : "Continuous AI runtime for architectural transparency and emotive depth.", tag: vibe === 'brainrot' ? "AURA_CORE" : "Autonomous Entity" },
                        { to: "/research", num: "06", title: vibe === 'brainrot' ? "BRAINROT_DEEP" : "Theory::Design", desc: vibe === 'brainrot' ? "MOGGING THE FUTURE. NO CAP. 👹" : "Guardrails, ethics, and the future of AI alignment.", tag: vibe === 'brainrot' ? "BASED_ETHICS" : "Philosophical Inquiry" },
                        { to: "/ask", num: "07", title: vibe === 'brainrot' ? "ASK_THE_AI" : "RAG // Ask", desc: vibe === 'brainrot' ? "CLOUD-NATIVE RAG DEPLOYED. VECTORS LOCKED IN. 👹" : "Cloud-native RAG on Google Cloud Run. Pre-baked ChromaDB, gemini-embedding-001, Gemini Flash synthesis.", tag: vibe === 'brainrot' ? "LIVE_DEPLOYMENT" : "Live // Cloud Run" }
                    ].map((proj, i) => (
                        <motion.div
                            key={proj.to}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 + (i * 0.1) }}
                            viewport={{ once: true }}
                        >
                            <Link
                                to={proj.to}
                                className={`group relative aspect-video glass-panel border transition-all block overflow-hidden p-8 text-center hover:scale-105 ${vibe === 'brainrot' ? 'border-violet-neon bg-violet/40 shadow-[0_0_40px_rgba(255,0,247,0.3)]' : 'celestial-border bg-slate/20 hover:bg-violet/5'}`}
                            >
                                <div className={`absolute inset-0 transition-opacity ${vibe === 'brainrot' ? 'lisa-frank-bg opacity-20' : 'bg-gradient-to-br from-violet/5 to-transparent opacity-0 group-hover:opacity-100'}`} />
                                <div className={`absolute top-4 left-4 font-serif text-[60px] italic select-none leading-none transition-all ${vibe === 'brainrot' ? 'text-white/20 animate-pulse' : 'text-violet/10'}`}>{proj.num}</div>
                                <div className="space-y-6 relative z-10">
                                    <h3 className={`text-4xl font-serif italic transition-all ${vibe === 'brainrot' ? 'text-rainbow drop-shadow-md' : 'text-ethereal group-hover:text-violet'}`}>{proj.title}</h3>
                                    <p className={`text-sm font-sans tracking-wide line-clamp-2 max-w-[280px] transition-all ${vibe === 'brainrot' ? 'text-white font-black uppercase' : 'text-ethereal/60'}`}>{proj.desc}</p>
                                    <div className="pt-4 flex items-center justify-center gap-3">
                                        <div className={`h-[1px] w-4 ${vibe === 'brainrot' ? 'bg-white' : 'bg-violet/30'}`} />
                                        <span className={`text-[10px] font-sans tracking-[0.2em] uppercase transition-colors ${vibe === 'brainrot' ? 'text-white font-bold' : 'text-violet/60'}`}>{proj.tag}</span>
                                        <div className={`h-[1px] w-4 ${vibe === 'brainrot' ? 'bg-white' : 'bg-violet/30'}`} />
                                    </div>
                                </div>
                                {vibe === 'brainrot' && (
                                    <div className="absolute bottom-2 right-2 text-2xl animate-bounce">👹</div>
                                )}
                            </Link>
                        </motion.div>
                    ))}
                </div>
            </div>

            {/* Background Decorations */}
            <div className="absolute top-1/2 left-0 -translate-y-1/2 w-full h-px bg-violet/5 -rotate-6 select-none pointer-events-none" />
            <div className="absolute top-1/2 left-0 -translate-y-1/2 w-full h-px bg-violet/5 rotate-12 select-none pointer-events-none" />
        </section>
    );
}
