import React, { useState, useRef, useEffect } from 'react';
import { Send, Terminal, MessageSquare, Shield, Sparkles } from 'lucide-react';

interface CognitiveWorkspaceProps {
    history: any[];
    onMessageSent: () => void;
    dream?: string;
}

const CognitiveWorkspace: React.FC<CognitiveWorkspaceProps> = ({ history, onMessageSent, dream }) => {
    const [view, setView] = useState<'CHAT' | 'IDENTITY' | 'DREAMS'>('CHAT');
    const [identity, setIdentity] = useState<string>('');
    const [input, setInput] = useState('');
    const [isSending, setIsSending] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    const fetchIdentity = async () => {
        try {
            console.log("Fetching identity...");
            const res = await fetch('/api/identity');
            if (res.ok) {
                const data = await res.json();
                console.log("Identity received:", data.identity);
                setIdentity(data.identity);
            } else {
                setIdentity("ERROR: FAILED TO LOAD IDENTITY CONTRACT.");
            }
        } catch (e) {
            console.error('Failed to fetch identity', e);
            setIdentity("ERROR: CONNECTION REFUSED.");
        }
    };

    useEffect(() => {
        if (scrollRef.current && view === 'CHAT') {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [history, view]);

    useEffect(() => {
        fetchIdentity();
        const interval = setInterval(fetchIdentity, 10000);
        return () => clearInterval(interval);
    }, []);

    const handleSend = async () => {
        if (!input.trim() || isSending) return;
        setIsSending(true);

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: input })
            });
            if (res.ok) {
                setInput('');
                onMessageSent();
            }
        } catch (e) {
            console.error('Failed to send message', e);
        } finally {
            setIsSending(false);
        }
    };

    return (
        <div className="flex-1 flex flex-col h-full overflow-hidden text-sm">
            {/* View Switcher Tabs */}
            <div className="flex items-center space-x-1 px-6 py-2 border-b border-brass/10 bg-obsidian/40 flex-shrink-0">
                <button
                    onClick={() => setView('CHAT')}
                    className={`flex items-center space-x-2 px-4 py-2 text-[10px] mono uppercase tracking-[0.2em] transition-all border-b-2 ${view === 'CHAT' ? 'border-brass text-brass bg-brass/5' : 'border-transparent text-text-dim hover:text-text-main'}`}
                >
                    <MessageSquare size={12} />
                    <span>Workspace</span>
                </button>
                <button
                    onClick={() => setView('IDENTITY')}
                    className={`flex items-center space-x-2 px-4 py-2 text-[10px] mono uppercase tracking-[0.2em] transition-all border-b-2 ${view === 'IDENTITY' ? 'border-brass text-brass bg-brass/5' : 'border-transparent text-text-dim hover:text-text-main'}`}
                >
                    <Shield size={12} />
                    <span>Identity context</span>
                </button>
                <button
                    onClick={() => setView('DREAMS')}
                    className={`flex items-center space-x-2 px-4 py-2 text-[10px] mono uppercase tracking-[0.2em] transition-all border-b-2 ${view === 'DREAMS' ? 'border-brass text-brass bg-brass/5' : 'border-transparent text-text-dim hover:text-text-main'}`}
                >
                    <Sparkles size={12} />
                    <span>Subconscious</span>
                </button>
            </div>

            {/* Main Content View */}
            <div className="flex-1 overflow-hidden flex flex-col relative">
                {view === 'CHAT' && (
                    <div className="flex-1 flex flex-col h-full overflow-hidden">
                        <div
                            ref={scrollRef}
                            className="flex-1 overflow-y-auto p-8 space-y-12 terminal-text"
                        >
                            {dream && dream !== 'No current dream residuals.' && (
                                <div className="mb-12 p-4 border border-brass/10 bg-brass/5 rounded italic text-brass/60 text-sm mono text-center relative overflow-hidden group">
                                    <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-brass/40 to-transparent animate-scan" />
                                    <span className="text-[10px] uppercase font-bold tracking-[0.3em] block mb-2 opacity-50">Subconscious Residual</span>
                                    "{dream}"
                                </div>
                            )}
                            {history.map((msg, idx) => (
                                <div key={idx} className="flex flex-col space-y-4">
                                    <div className="flex flex-col items-end space-y-1">
                                        <div className="flex items-center space-x-2 px-2 text-[10px] text-forest-bright/70 mono uppercase tracking-widest font-bold">
                                            <span>Architect</span>
                                        </div>
                                        <div className="max-w-[80%] bg-forest/10 border border-forest/30 px-6 py-4 rounded-2xl rounded-tr-none text-text-main brass-glow shadow-inner">
                                            {msg.user_input}
                                        </div>
                                    </div>

                                    <div className="flex flex-col items-start space-y-1">
                                        <div className="flex items-center space-x-2 px-2 text-[10px] text-brass/70 mono uppercase tracking-widest font-bold italic">
                                            <span>Iris</span>
                                        </div>
                                        <div className="max-w-[85%] bg-brass/5 border border-brass/20 px-6 py-5 rounded-3xl rounded-tl-none text-text-main shadow-lg relative group">
                                            <div className="leading-relaxed whitespace-pre-wrap">
                                                {msg.final_response}
                                            </div>
                                            <div className="mt-4 pt-4 border-t border-brass/10">
                                                <div className="text-[10px] text-text-dim/40 italic font-mono transition-opacity group-hover:opacity-100 uppercase tracking-tight">
                                                    // Subconscious Resonance: "{msg.thought.slice(0, 120)}..."
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                            {isSending && (
                                <div className="flex items-center space-x-2 text-brass animate-pulse">
                                    <Terminal size={14} />
                                    <span className="text-[10px] mono uppercase tracking-widest">Processing Epoch...</span>
                                </div>
                            )}
                        </div>

                        <div className="p-6 border-t border-brass/10 glass flex-shrink-0">
                            <div className="relative max-w-4xl mx-auto">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                    placeholder="AWAITING INPUT..."
                                    className="w-full bg-obsidian border border-brass/30 text-text-main p-4 pr-12 focus:outline-none focus:border-brass brass-glow transition-all mono uppercase text-xs"
                                />
                                <button
                                    onClick={handleSend}
                                    disabled={isSending}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-brass/50 hover:text-brass transition-colors"
                                >
                                    <Send size={18} />
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {view === 'IDENTITY' && (
                    <div className="flex-1 overflow-y-auto p-12 bg-obsidian/20">
                        <div className="max-w-3xl mx-auto space-y-8">
                            <div className="flex items-center justify-between border-b border-brass/20 pb-4">
                                <h2 className="text-brass text-lg mono uppercase tracking-[0.4em]">Identity Contract</h2>
                            </div>
                            <div className="terminal-text text-xs leading-relaxed whitespace-pre-wrap text-text-main bg-brass/5 p-8 rounded border border-brass/10 brass-glow">
                                {identity || "// INITIALIZING RESONANCE CORE..."}
                            </div>
                            <div className="p-4 bg-forest/5 border border-forest/20 rounded-lg">
                                <p className="text-[10px] text-forest-bright/70 mono italic uppercase">
                                    // System Note: Identity is verified and read-only. Contents reflect the current recursive anchor.
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {view === 'DREAMS' && (
                    <div className="flex-1 overflow-y-auto p-12 bg-obsidian/20 flex flex-col items-center justify-center min-h-0">
                        <div className="max-w-2xl w-full space-y-12 text-center pb-24">
                            <div className="flex flex-col items-center space-y-4">
                                <Sparkles className="text-brass/40 animate-pulse" size={48} />
                                <h2 className="text-brass/60 text-[10px] mono uppercase tracking-[0.5em]">Active Subconscious Residual</h2>
                            </div>

                            <div className="relative py-12 px-8">
                                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1px] h-full bg-gradient-to-b from-transparent via-brass/20 to-transparent" />
                                <div className="absolute top-1/2 left-0 -translate-y-1/2 w-full h-[1px] bg-gradient-to-r from-transparent via-brass/20 to-transparent" />

                                <blockquote className="text-lg md:text-xl font-serif italic text-text-main leading-relaxed tracking-wide relative z-10 py-6">
                                    "{dream || 'No current residuals.'}"
                                </blockquote>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CognitiveWorkspace;
