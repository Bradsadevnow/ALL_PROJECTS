import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles } from 'lucide-react';

interface AuraMaxToggleProps {
    vibe: 'tech' | 'normal' | 'brainrot';
    setVibe: (v: 'tech' | 'normal' | 'brainrot') => void;
    onTriggerRipple: () => void;
}

export const AuraMaxToggle = ({ vibe, setVibe, onTriggerRipple }: AuraMaxToggleProps) => {
    const [isHovered, setIsHovered] = useState(false);

    const handleToggle = () => {
        if (vibe !== 'brainrot') {
            onTriggerRipple();
            setTimeout(() => setVibe('brainrot'), 200);
        } else {
            setVibe('tech');
        }
    };

    return (
        <div className="relative group">
            {/* Hover Sparkles */}
            <AnimatePresence>
                {(isHovered || vibe === 'brainrot') && (
                    <motion.div
                        className="absolute inset-0 pointer-events-none"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                    >
                        {[...Array(vibe === 'brainrot' ? 40 : 12)].map((_, i) => (
                            <motion.div
                                key={i}
                                className="absolute"
                                style={{ color: ['#ff00f7', '#00d2ff', '#9aff00', '#ff0055', '#00ffcc'][i % 5] }}
                                initial={{
                                    x: "50%",
                                    y: "50%",
                                    scale: 0,
                                    rotate: 0
                                }}
                                animate={{
                                    x: `${50 + (Math.random() - 0.5) * (vibe === 'brainrot' ? 600 : 200)}%`,
                                    y: `${50 + (Math.random() - 0.5) * (vibe === 'brainrot' ? 600 : 200)}%`,
                                    scale: [0, vibe === 'brainrot' ? 2.5 : 1.5, 0],
                                    rotate: Math.random() * 720
                                }}
                                transition={{
                                    duration: vibe === 'brainrot' ? Math.random() * 0.5 + 0.3 : 0.8,
                                    repeat: Infinity,
                                    delay: Math.random() * 0.5,
                                    ease: "easeOut"
                                }}
                            >
                                {vibe === 'brainrot' ? (
                                    <span className="text-2xl">👹</span>
                                ) : (
                                    <Sparkles size={16} />
                                )}
                            </motion.div>
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>

            <motion.button
                onClick={handleToggle}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
                whileHover={{ scale: 1.1, rotate: vibe === 'brainrot' ? [0, -5, 5, 0] : 0 }}
                whileTap={{ scale: 0.9 }}
                className={`
                    px-16 py-6 rounded-full border-4 transition-all duration-300
                    flex items-center gap-6 text-xl font-black tracking-[0.6em] uppercase
                    ${vibe === 'brainrot'
                        ? 'lisa-frank-bg border-white shadow-[0_0_100px_rgba(255,0,247,0.8)] animate-vibrate scale-110 h-32'
                        : 'bg-void text-violet border-violet/40 hover:border-violet/80 hover:shadow-[0_0_30px_rgba(139,92,246,0.5)]'
                    }
                `}
            >
                <div className={`flex items-center gap-4 ${vibe === 'brainrot' ? 'text-rainbow drop-shadow-[2px_2px_0px_rgba(0,0,0,1)]' : ''}`}>
                    <Sparkles size={24} className={vibe === 'brainrot' ? 'animate-spin-slow' : ''} />
                    {vibe === 'brainrot' ? "MOGGING_THE_OPPS" : "CLICK FOR AURA"}
                    <Sparkles size={24} className={vibe === 'brainrot' ? 'animate-spin-slow' : ''} />
                </div>
            </motion.button>
        </div>
    );
};
