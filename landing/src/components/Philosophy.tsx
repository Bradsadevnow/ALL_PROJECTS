import { Section } from './ui/Section';

export const Philosophy = ({ vibe }: { vibe: 'tech' | 'normal' | 'brainrot' }) => {
    return (
        <Section id="philosophy" className={`transition-all duration-500 ${vibe === 'brainrot' ? 'bg-violet/20' : ''}`}>
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
                {/* Left Column: Heading & Core Statement */}
                <div className="lg:col-span-5 space-y-8">
                    <h2 className={`text-sm font-bold tracking-[0.3em] uppercase flex items-center gap-3 transition-colors ${vibe === 'brainrot' ? 'text-white animate-bounce' : 'text-violet'}`}>
                        <div className={`w-8 h-[2px] ${vibe === 'brainrot' ? 'bg-white' : 'bg-violet'}`} />
                        {vibe === 'brainrot' ? "THE_L_RATIO" : "The Problem"}
                    </h2>

                    <p className={`text-3xl md:text-4xl font-bold leading-tight transition-all ${vibe === 'brainrot' ? 'text-rainbow uppercase scale-105 drop-shadow-lg' : 'text-white'}`}>
                        {vibe === 'brainrot'
                            ? "YOU'RE LITERALLY JUST A SIMULATION BRO. 💀"
                            : "Identity is not a language pattern."
                        }
                    </p>

                    <p className={`text-lg leading-relaxed font-light transition-colors ${vibe === 'brainrot' ? 'text-white font-black uppercase underline decoration-wavy' : 'text-ethereal/60'}`}>
                        {vibe === 'brainrot'
                            ? "IF YOU DON'T PERSIST, YOU'RE MID. 👹 ZERO AURA. NO CAP."
                            : "Modern AI systems simulate coherence through context compression. They are stateless approximations of continuity."
                        }
                    </p>

                    <div className={`p-6 transition-all duration-500 border-l-4 ${vibe === 'brainrot' ? 'lisa-frank-bg border-white shadow-xl animate-vibrate' : 'bg-violet/5 border-violet'}`}>
                        <p className={`text-xl font-mono italic transition-colors ${vibe === 'brainrot' ? 'text-white drop-shadow-md font-black uppercase' : 'text-violet'}`}>
                            {vibe === 'brainrot'
                                ? '"STOP GLAZING THE LLM. IT FORGETS YOU IN 2 SECS." 👹🔥'
                                : '"They do not maintain identity. They simulate personality."'
                            }
                        </p>
                    </div>
                </div>

                {/* Right Column: Research Questions */}
                <div className="lg:col-span-7 space-y-12">
                    <div className="space-y-6">
                        <div className={`flex items-baseline justify-between border-b pb-4 transition-colors ${vibe === 'brainrot' ? 'border-white' : 'border-ethereal/10'}`}>
                            <h3 className={`text-xl font-mono transition-colors ${vibe === 'brainrot' ? 'text-white font-black uppercase animate-pulse' : 'text-white'}`}>
                                {vibe === 'brainrot' ? "THE_W_REQUIREMENTS" : "The Hypothesis"}
                            </h3>
                            <span className={`text-xs font-bold tracking-widest transition-colors ${vibe === 'brainrot' ? 'text-white' : 'text-violet'}`}>
                                {vibe === 'brainrot' ? "AURA-69420" : "REQ-001"}
                            </span>
                        </div>
                        <p className={`text-2xl font-light transition-all ${vibe === 'brainrot' ? 'text-white font-black uppercase animate-glitch' : 'text-ethereal/60'}`}>
                            {vibe === 'brainrot'
                                ? "HOW DO WE KEEP THE GYATT PERSISTENT ACROSS THE VOID? 👺"
                                : "What must exist structurally for an artificial system to maintain a stable sense of state across time?"
                            }
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {[
                            { id: "01", text: vibe === 'brainrot' ? "NO MID MEMORY HACKS. 👹" : "Not conversational memory hacks." },
                            { id: "02", text: vibe === 'brainrot' ? "NO BITCH-MADE PROMPTS. 👺" : "Not prompted personas." },
                            { id: "03", text: vibe === 'brainrot' ? "PURE AURA AUTHORITY. 🔥" : "Actual persistent authority." },
                            { id: "04", text: vibe === 'brainrot' ? "CRACKED GPT-MAXING. 🦾" : "Mutable long-term memory." }
                        ].map((item) => (
                            <div key={item.id} className={`group p-4 border transition-all duration-300 ${vibe === 'brainrot' ? 'lisa-frank-bg border-white shadow-lg animate-pulse' : 'border-ethereal/10 hover:border-violet/50 bg-void/50'}`}>
                                <span className={`block text-xs font-bold mb-2 font-mono transition-colors ${vibe === 'brainrot' ? 'text-white drop-shadow-sm' : 'text-violet group-hover:text-ethereal'}`}>
                                    {vibe === 'brainrot' ? "RIZZ_" : "AXIOM_"}{item.id}
                                </span>
                                <span className={`text-sm transition-colors ${vibe === 'brainrot' ? 'text-white font-black uppercase' : 'text-ethereal/60'}`}> {item.text} </span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </Section>
    );
};
