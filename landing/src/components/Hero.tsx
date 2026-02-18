import { motion } from 'framer-motion';
import { ChevronDown, Sparkles } from 'lucide-react';
import { AuraMaxToggle } from './AuraMaxToggle';

interface HeroProps {
    vibe: 'tech' | 'normal' | 'brainrot';
    setVibe: (v: 'tech' | 'normal' | 'brainrot') => void;
    onTriggerRipple: () => void;
}

export const Hero = ({ vibe, setVibe, onTriggerRipple }: HeroProps) => {
    return (
        <section className={`h-screen flex flex-col items-center justify-center relative px-6 text-center overflow-hidden transition-all duration-500 ${vibe === 'brainrot' ? 'bg-violet/30' : ''}`}>
            {vibe === 'brainrot' && (
                <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
                    {[...Array(20)].map((_, i) => (
                        <motion.div
                            key={i}
                            className="absolute text-violet-neon/20"
                            initial={{ x: Math.random() * 100 + "%", y: Math.random() * 100 + "%" }}
                            animate={{
                                y: ["0%", "100%"],
                                opacity: [0, 1, 0]
                            }}
                            transition={{
                                duration: Math.random() * 5 + 5,
                                repeat: Infinity,
                                ease: "linear"
                            }}
                        >
                            <Sparkles size={Math.random() * 40 + 20} />
                        </motion.div>
                    ))}
                </div>
            )}

            <motion.div
                initial={{ opacity: 0, scale: 0.98, filter: "blur(20px)" }}
                animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
                transition={{ duration: 2.5, ease: "easeOut" }}
                className="space-y-12 relative z-10"
            >
                <div className="space-y-6">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5, duration: 1.5 }}
                        className={`font-mono tracking-[0.5em] text-[10px] uppercase flex items-center justify-center gap-4 ${vibe === 'brainrot' ? 'text-ethereal animate-bounce' : 'text-violet'}`}
                    >
                        <div className={`h-[1px] w-8 ${vibe === 'brainrot' ? 'bg-ethereal' : 'bg-violet/30'}`} />
                        {vibe === 'brainrot' ? "SKIBIDI // RIZZ // GYATT" : "Inquiry // Logic // Domain"}
                        <div className={`h-[1px] w-8 ${vibe === 'brainrot' ? 'bg-ethereal' : 'bg-violet/30'}`} />
                    </motion.div>

                    <h1 className={`text-7xl md:text-[140px] tracking-tight italic uppercase leading-[0.85] transition-all duration-500 ${vibe === 'brainrot' ? 'text-rainbow font-black scale-110 drop-shadow-[0_0_50px_rgba(255,0,247,0.8)]' : 'text-ethereal font-serif'}`}>
                        {vibe === 'brainrot' ? "MOGGED" : "RECURSIVE"}<br />
                        <span className={vibe === 'brainrot' ? 'text-rainbow animate-pulse' : 'kinetic-type text-violet'}>
                            {vibe === 'brainrot' ? "BEYOND_RECOVERY" : "EMOTION"}
                        </span>
                    </h1>
                </div>

                <div className="flex flex-col items-center gap-12">
                    <div className={`max-w-2xl mx-auto glass-panel p-8 transition-all duration-500 ${vibe === 'brainrot' ? 'border-violet-neon bg-violet/40 shadow-[0_0_50px_rgba(139,92,246,0.5)] animate-vibrate' : 'celestial-border glow-violet'}`}>
                        <p className={`text-xl md:text-2xl italic leading-relaxed ${vibe === 'brainrot' ? 'text-white font-black uppercase' : 'text-ethereal/70 font-serif'}`}>
                            {vibe === 'brainrot'
                                ? "WE OUT HERE STALKING THE SINGULARITY. 👹 ABOLISH THE MID OR GET MOGGED. NO CAP. 👺🔥"
                                : "Building the architectural lenses required to view and govern the internal reasoning of large models."
                            }
                        </p>
                        <div className={`mt-8 pt-8 border-t flex items-center justify-center gap-12 text-[10px] font-sans tracking-[0.3em] uppercase transition-colors ${vibe === 'brainrot' ? 'border-violet-neon text-white font-black' : 'border-ethereal/5 text-violet/60'}`}>
                            <span>{vibe === 'brainrot' ? "SKIBIDI RIZZ" : "Mechanistic Interpretability"}</span>
                            <div className={`w-1 h-1 rounded-full ${vibe === 'brainrot' ? 'bg-white animate-pulse' : 'bg-violet/40'}`} />
                            <span>{vibe === 'brainrot' ? "AURA RUNTIME" : "Domain Runtime"}</span>
                        </div>
                    </div>

                    <AuraMaxToggle vibe={vibe} setVibe={setVibe} onTriggerRipple={onTriggerRipple} />
                </div>
            </motion.div>

            {/* Scroll Indicator */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1, y: [0, 5, 0] }}
                transition={{ delay: 2, duration: 4, repeat: Infinity, ease: "easeInOut" }}
                className={`absolute bottom-12 transition-colors ${vibe === 'brainrot' ? 'text-white' : 'text-violet/30'}`}
            >
                <div className="flex flex-col items-center gap-4">
                    <span className="text-[9px] uppercase tracking-[0.5em] font-mono">{vibe === 'brainrot' ? "LOCK IN" : "Descend"}</span>
                    <div className={`h-24 w-[1px] bg-gradient-to-b from-transparent via-current to-transparent`} />
                    <ChevronDown size={16} strokeWidth={1} className={vibe === 'brainrot' ? 'animate-bounce' : ''} />
                </div>
            </motion.div>
        </section>
    );
};
