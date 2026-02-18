import { motion, AnimatePresence } from 'framer-motion';
import { Box, Github } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useState } from 'react';

export function Navbar({ vibe }: { vibe: 'tech' | 'normal' | 'brainrot' }) {
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    return (
        <motion.header
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            className={`fixed top-0 left-0 right-0 z-50 border-b transition-all duration-500 ${vibe === 'brainrot' ? 'border-violet-neon bg-violet/40 shadow-lg' : 'border-ethereal/5 bg-void/60 backdrop-blur-md'}`}
        >
            <nav className="max-w-6xl mx-auto px-6 h-20 flex items-center justify-between">
                <Link to="/" className={`text-xl font-serif italic tracking-tighter group transition-all duration-500 ${vibe === 'brainrot' ? 'text-rainbow scale-110 drop-shadow-md' : 'text-ethereal'}`}>
                    RECURSIVE<span className={`transition-opacity ${vibe === 'brainrot' ? 'text-white' : 'text-violet opacity-60 group-hover:opacity-100'}`}>EMOTION</span>
                </Link>

                <div className="flex items-center gap-12">
                    <div
                        className="relative group"
                        onMouseEnter={() => setIsMenuOpen(true)}
                        onMouseLeave={() => setIsMenuOpen(false)}
                    >
                        <button className={`transition-all flex items-center gap-2 group/btn font-sans text-[10px] tracking-[0.3em] uppercase ${vibe === 'brainrot' ? 'text-white font-black animate-pulse' : 'text-ethereal/60 hover:text-violet'}`}>
                            <Box size={14} className={`transition-transform ${vibe === 'brainrot' ? 'animate-spin-slow' : 'group-hover/btn:rotate-12'}`} />
                            {vibe === 'brainrot' ? "MOG_LOCK" : "Projects"}
                        </button>

                        <AnimatePresence>
                            {isMenuOpen && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10, filter: "blur(10px)" }}
                                    animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                                    exit={{ opacity: 0, y: 10, filter: "blur(10px)" }}
                                    className={`absolute top-full right-0 mt-4 w-64 p-2 shadow-2xl z-50 overflow-hidden ${vibe === 'brainrot' ? 'lisa-frank-bg border-2 border-white rounded-none' : 'glass-panel rounded'}`}
                                >
                                    <div className="space-y-1">
                                        {[
                                            { path: '/projects/t-scan', label: vibe === 'brainrot' ? 'SKIBIDI_SCAN' : 'T-Scan Research', id: '01' },
                                            { path: '/projects/halcyon', label: vibe === 'brainrot' ? 'HALCYON_GYATT' : 'Halcyon Logic', id: '02' },
                                            { path: '/projects/shared-workbench', label: vibe === 'brainrot' ? 'RIZZ_BENCH' : 'Shared Workbench', id: '03' },
                                            { path: '/projects/bob', label: vibe === 'brainrot' ? 'BOB_THE_MOGGER' : 'Bob: Visual Shell', id: '04' }
                                        ].map((project) => (
                                            <Link
                                                key={project.path}
                                                to={project.path}
                                                className={`flex items-center justify-between px-4 py-3 rounded transition-all group/item ${vibe === 'brainrot' ? 'hover:bg-white/20' : 'hover:bg-violet/10'}`}
                                                onClick={() => setIsMenuOpen(false)}
                                            >
                                                <span className={`text-[10px] font-inter tracking-tighter transition-colors ${vibe === 'brainrot' ? 'text-white/40 group-hover/item:text-white' : 'text-violet/40 group-hover/item:text-violet/60'}`}>{project.id}</span>
                                                <span className={`text-sm font-inter transition-colors ${vibe === 'brainrot' ? 'text-white font-black uppercase' : 'text-ethereal/80 group-hover/item:text-ethereal'}`}>{project.label}</span>
                                            </Link>
                                        ))}
                                    </div>
                                    <div className={`mt-4 p-4 border-t ${vibe === 'brainrot' ? 'border-white/20' : 'border-ethereal/5'}`}>
                                        <Link to="/research" className={`text-[9px] font-inter tracking-[0.3em] uppercase transition-all flex items-center gap-2 ${vibe === 'brainrot' ? 'text-rainbow font-black scale-110 animate-bounce' : 'text-white hover:text-violet'}`}>
                                            <div className={`w-1 h-1 rounded-full animate-pulse ${vibe === 'brainrot' ? 'bg-white shadow-[0_0_10px_white]' : 'bg-white'}`} />
                                            {vibe === 'brainrot' ? "AURA_RESEARCH" : "Theory & Design"}
                                        </Link>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    <a
                        href="https://github.com/Bradsadevnow"
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`transition-all ${vibe === 'brainrot' ? 'text-white scale-125 animate-vibrate' : 'text-ethereal/40 hover:text-ethereal'}`}
                    >
                        <Github size={20} strokeWidth={1} />
                    </a>
                </div>

                <div className="hidden lg:flex items-center gap-6">
                    <div className={`flex items-center gap-2 px-3 py-1 border transition-all ${vibe === 'brainrot' ? 'border-white bg-white/20 animate-pulse' : 'border-violet/10 bg-violet/5'}`}>
                        <div className={`w-1 h-1 animate-pulse ${vibe === 'brainrot' ? 'bg-white' : 'bg-violet'}`} />
                        <span className={`text-[9px] font-sans tracking-[0.3em] uppercase ${vibe === 'brainrot' ? 'text-white font-black' : 'text-violet'}`}>
                            {vibe === 'brainrot' ? "STATUS::MAXED" : "Status::Connected"}
                        </span>
                    </div>
                </div>
            </nav>
        </motion.header>
    );
}
