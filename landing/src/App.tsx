import { GridBackground } from './components/ui/GridBackground';
import { Hero } from './components/Hero';
import { Philosophy } from './components/Philosophy';
import { System } from './components/System';
import { Architect } from './components/Architect';
import { Navbar } from './components/Navbar';
import { Projects } from './components/Projects';
import { Linkedin, Twitter, Facebook } from 'lucide-react';
import { TScan } from './pages/TScan';
import { SharedWorkbench } from './pages/SharedWorkbench';
import { Bob } from './pages/Bob';
import { Halcyon } from './pages/Halcyon';
import { Research } from './pages/Research';
import { Iris } from './pages/Iris';
import { Routes, Route, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';

function Home({ vibe, setVibe, onTriggerRipple }: {
    vibe: 'tech' | 'normal' | 'brainrot',
    setVibe: (v: 'tech' | 'normal' | 'brainrot') => void,
    onTriggerRipple: () => void
}) {
    return (
        <main className={`pt-20 transition-all duration-500 ${vibe === 'brainrot' ? 'intense-glitter' : ''}`}>
            <Hero vibe={vibe} setVibe={setVibe} onTriggerRipple={onTriggerRipple} />
            <Projects vibe={vibe} />
            <Philosophy vibe={vibe} />
            <System vibe={vibe} />
            <Architect vibe={vibe} />
        </main>
    );
}

export default function App() {
    const { pathname, hash } = useLocation();
    const [vibe, setVibe] = useState<'tech' | 'normal' | 'brainrot'>('tech');
    const [ripples, setRipples] = useState<{ id: number, x: number, y: number }[]>([]);

    const triggerRipple = (x: number = window.innerWidth / 2, y: number = window.innerHeight / 2) => {
        const id = Date.now();
        setRipples([...ripples, { id, x, y }]);
        setTimeout(() => {
            setRipples((prev: { id: number, x: number, y: number }[]) => prev.filter((r: { id: number, x: number, y: number }) => r.id !== id));
        }, 1000);
    };

    useEffect(() => {
        if (hash) {
            const element = document.getElementById(hash.replace('#', ''));
            if (element) {
                element.scrollIntoView({ behavior: 'smooth' });
            }
        } else {
            window.scrollTo(0, 0);
        }
    }, [pathname, hash]);

    return (
        <div className={`min-h-screen relative overflow-x-hidden selection:bg-violet/30 selection:text-ethereal transition-all duration-500 ${vibe === 'brainrot' ? 'bg-violet/20' : ''}`}>
            <GridBackground />

            {/* Ripple Layer */}
            <div className="fixed inset-0 pointer-events-none z-[9999] overflow-hidden">
                {ripples.map((ripple: { id: number, x: number, y: number }) => (
                    <div
                        key={ripple.id}
                        className="absolute w-[100vmax] h-[100vmax] -translate-x-1/2 -translate-y-1/2 rounded-full lisa-frank-bg animate-ripple"
                        style={{ left: ripple.x, top: ripple.y }}
                    />
                ))}
            </div>

            <Navbar vibe={vibe} />

            <Routes>
                <Route path="/" element={<Home vibe={vibe} setVibe={setVibe} onTriggerRipple={() => triggerRipple()} />} />
                <Route path="/projects/t-scan" element={<TScan />} />
                <Route path="/projects/shared-workbench" element={<SharedWorkbench />} />
                <Route path="/projects/bob" element={<Bob />} />
                <Route path="/projects/halcyon" element={<Halcyon />} />
                <Route path="/projects/iris" element={<Iris />} />
                <Route path="/research" element={<Research vibe={vibe} setVibe={setVibe} />} />
            </Routes>

            <footer className="py-12 text-center border-t border-violet/10 bg-void/80 backdrop-blur-md relative z-10 space-y-6">
                <div className="flex justify-center gap-8">
                    <a href="https://www.linkedin.com/in/bradley-bates-792871387/" target="_blank" rel="noopener noreferrer" className="text-ethereal/40 hover:text-violet transition-colors duration-300">
                        <Linkedin size={20} strokeWidth={1} />
                    </a>
                    <a href="https://x.com/recursive_smart" target="_blank" rel="noopener noreferrer" className="text-ethereal/40 hover:text-violet transition-colors duration-300">
                        <Twitter size={20} strokeWidth={1} />
                    </a>
                    <a href="https://www.facebook.com/profile.php?id=61575558568159" target="_blank" rel="noopener noreferrer" className="text-ethereal/40 hover:text-violet transition-colors duration-300">
                        <Facebook size={20} strokeWidth={1} />
                    </a>
                </div>
                <p className="text-[10px] text-ethereal/40 uppercase tracking-[0.4em] font-mono hover:text-violet transition-colors duration-300">
                    © 2026 Recursive Emotion // Continuity Guaranteed
                </p>
            </footer>
        </div>
    );
}
