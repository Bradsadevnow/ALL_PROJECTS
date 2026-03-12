import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const CYCLING = [
    "What is the Mirror Trap?",
    "How does Bob prevent illegal MTG moves?",
    "Explain the sleep cycle memory consolidation pattern.",
    "How does the Iris emotive physics engine work?",
    "What is the difference between STM and LTM in these systems?",
];

export function AskStrip({ vibe }: { vibe: 'tech' | 'normal' | 'brainrot' }) {
    const [input, setInput] = useState('');
    const [cycleIdx, setCycleIdx] = useState(0);
    const navigate = useNavigate();

    useEffect(() => {
        const t = setInterval(() => setCycleIdx(i => (i + 1) % CYCLING.length), 3500);
        return () => clearInterval(t);
    }, []);

    function handleSubmit() {
        const q = input.trim();
        if (!q) return;
        navigate(`/ask?q=${encodeURIComponent(q)}`);
    }

    function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
        if (e.key === 'Enter') { e.preventDefault(); handleSubmit(); }
    }

    return (
        <motion.section
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className={`py-24 px-8 border-y transition-colors ${vibe === 'brainrot' ? 'border-violet-neon/40' : 'border-violet/10'}`}
        >
            <div className="max-w-4xl mx-auto space-y-8">

                <div className="flex items-center justify-between">
                    <span className={`font-mono text-[10px] tracking-[0.5em] uppercase ${vibe === 'brainrot' ? 'text-white font-black animate-pulse' : 'text-violet'}`}>
                        {vibe === 'brainrot' ? '// PORTFOLIO::LOCKED_IN' : '// portfolio::queryable'}
                    </span>
                    <span className="flex items-center gap-2 font-mono text-[10px] text-ethereal/30 uppercase tracking-[0.3em]">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-400/70 animate-pulse" />
                        {vibe === 'brainrot' ? 'LIVE · CRACKED DEPLOYMENT' : 'Live · Cloud Run'}
                    </span>
                </div>

                <p className={`text-4xl md:text-6xl italic leading-tight transition-all ${vibe === 'brainrot' ? 'text-rainbow font-black drop-shadow-[0_0_20px_rgba(255,0,247,0.4)]' : 'text-ethereal/80 font-serif'}`}>
                    {vibe === 'brainrot' ? 'THIS PORTFOLIO' : 'This portfolio'}<br />
                    <span className={vibe === 'brainrot' ? 'text-white' : 'text-violet'}>
                        {vibe === 'brainrot' ? 'ANSWERS QUESTIONS. 👹' : 'answers questions.'}
                    </span>
                </p>

                <div className={`glass-panel border backdrop-blur-md transition-all ${vibe === 'brainrot' ? 'border-violet-neon bg-violet/30 shadow-[0_0_30px_rgba(139,92,246,0.3)]' : 'border-violet/20 bg-void/40'}`}>
                    <div className="flex items-center gap-3 px-6 py-5">
                        <span className={`font-mono text-sm flex-shrink-0 ${vibe === 'brainrot' ? 'text-white' : 'text-violet/40'}`}>›</span>
                        <input
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder={CYCLING[cycleIdx]}
                            className={`flex-1 bg-transparent font-mono text-sm focus:outline-none transition-colors ${vibe === 'brainrot' ? 'text-white placeholder-white/30 font-black' : 'text-ethereal/80 placeholder-ethereal/20'}`}
                        />
                        <button
                            onClick={handleSubmit}
                            className={`text-[10px] font-mono tracking-[0.3em] uppercase transition-all flex-shrink-0 border px-3 py-1.5 ${vibe === 'brainrot' ? 'border-white text-white hover:bg-white hover:text-void font-black' : 'border-violet/20 text-violet/50 hover:text-violet hover:border-violet/50'}`}
                        >
                            {vibe === 'brainrot' ? 'LOCK IN' : 'Ask'}
                        </button>
                    </div>
                </div>

                <p className={`text-[10px] font-mono uppercase tracking-widest ${vibe === 'brainrot' ? 'text-white/40' : 'text-ethereal/20'}`}>
                    {vibe === 'brainrot'
                        ? 'RAG OVER ESSAYS · ARCH DOCS · PROJECT READMES · DESIGN DECISIONS'
                        : 'RAG over essays · architecture docs · project READMEs · design decisions'}
                </p>

            </div>
        </motion.section>
    );
}
