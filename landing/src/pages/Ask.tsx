import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Send, FileText, Loader } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

const RAG_API_URL = import.meta.env.VITE_RAG_API_URL ?? 'http://localhost:8080';

interface Source {
    title: string;
    path: string;
    excerpt: string;
}

interface Message {
    id: number;
    question: string;
    answer: string;
    sources: Source[];
}

const SUGGESTED = [
    "What is the Mirror Trap?",
    "How does the Iris emotive physics engine work?",
    "Explain the sleep cycle memory consolidation pattern.",
    "How does Bob prevent the AI from making illegal MTG moves?",
    "What is the difference between STM and LTM in these systems?",
];

export function Ask() {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const bottomRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);
    const [searchParams] = useSearchParams();

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, loading]);

    // Auto-submit question passed via ?q= from AskStrip
    useEffect(() => {
        const q = searchParams.get('q');
        if (q) submit(q);
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    async function submit(question: string) {
        const q = question.trim();
        if (!q || loading) return;

        setInput('');
        setError('');
        setLoading(true);

        try {
            const res = await fetch(`${RAG_API_URL}/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: q }),
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail ?? `HTTP ${res.status}`);
            }

            const data = await res.json();
            setMessages(prev => [...prev, {
                id: Date.now(),
                question: q,
                answer: data.answer,
                sources: data.sources ?? [],
            }]);
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : 'Request failed');
        } finally {
            setLoading(false);
            setTimeout(() => inputRef.current?.focus(), 50);
        }
    }

    function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            submit(input);
        }
    }

    return (
        <main className="pt-32 pb-24 px-6 min-h-screen bg-void relative overflow-hidden">
            <div className="max-w-3xl mx-auto space-y-16">

                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-6"
                >
                    <div className="flex items-center gap-3 font-mono tracking-[0.5em] text-[10px] text-violet uppercase">
                        <MessageSquare size={16} strokeWidth={1} />
                        <span>Ask::Recursive_Emotion</span>
                    </div>
                    <h1 className="text-6xl md:text-8xl tracking-tight italic leading-[0.85] text-ethereal font-serif">
                        ASK<br />
                        <span className="text-violet opacity-60">ANYTHING</span>
                    </h1>
                    <p className="text-ethereal/50 font-mono text-sm leading-relaxed max-w-xl">
                        Retrieval-augmented search over the research essays, architecture docs, and project READMEs in this portfolio. Answers are grounded in the actual source material.
                    </p>
                </motion.div>

                {/* Suggested questions (shown only before first message) */}
                <AnimatePresence>
                    {messages.length === 0 && !loading && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0, height: 0 }}
                            className="space-y-3"
                        >
                            <span className="text-[10px] font-mono tracking-[0.3em] uppercase text-ethereal/30">
                                Suggested
                            </span>
                            <div className="flex flex-wrap gap-2">
                                {SUGGESTED.map((q) => (
                                    <button
                                        key={q}
                                        onClick={() => submit(q)}
                                        className="px-3 py-2 text-[11px] font-mono border border-violet/20 text-ethereal/50 hover:text-ethereal hover:border-violet/60 hover:bg-violet/5 transition-all rounded text-left"
                                    >
                                        {q}
                                    </button>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Message thread */}
                <div className="space-y-10">
                    <AnimatePresence initial={false}>
                        {messages.map((msg) => (
                            <motion.div
                                key={msg.id}
                                initial={{ opacity: 0, y: 16, filter: 'blur(8px)' }}
                                animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                                transition={{ duration: 0.4, ease: 'easeOut' }}
                                className="space-y-4"
                            >
                                {/* Question */}
                                <div className="flex items-start gap-3">
                                    <div className="w-1 h-1 mt-2 bg-violet rounded-full flex-shrink-0" />
                                    <p className="text-ethereal/70 font-mono text-sm italic">{msg.question}</p>
                                </div>

                                {/* Answer */}
                                <div className="glass-panel p-6 space-y-5 border border-violet/10 bg-slate/10">
                                    <p className="text-ethereal/90 leading-relaxed text-sm whitespace-pre-wrap font-serif italic text-lg">
                                        {msg.answer}
                                    </p>

                                    {/* Sources */}
                                    {msg.sources.length > 0 && (
                                        <div className="pt-4 border-t border-ethereal/5 space-y-2">
                                            <span className="text-[9px] font-mono tracking-[0.4em] uppercase text-violet/50">
                                                Sources
                                            </span>
                                            <div className="flex flex-wrap gap-2">
                                                {msg.sources.map((src) => (
                                                    <div
                                                        key={src.path}
                                                        title={src.excerpt}
                                                        className="flex items-center gap-1.5 px-2 py-1 border border-violet/15 bg-violet/5 text-[10px] font-mono text-ethereal/50 rounded"
                                                    >
                                                        <FileText size={10} strokeWidth={1} className="text-violet/40" />
                                                        {src.title}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {/* Loading state */}
                    <AnimatePresence>
                        {loading && (
                            <motion.div
                                initial={{ opacity: 0, y: 8 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                                className="flex items-center gap-3 text-violet/60"
                            >
                                <Loader size={14} strokeWidth={1} className="animate-spin" />
                                <span className="text-[10px] font-mono tracking-[0.3em] uppercase">
                                    Retrieving...
                                </span>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Error */}
                    <AnimatePresence>
                        {error && (
                            <motion.p
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="text-[11px] font-mono text-red-400/70 border border-red-400/20 px-4 py-2 rounded"
                            >
                                Error: {error}
                            </motion.p>
                        )}
                    </AnimatePresence>

                    <div ref={bottomRef} />
                </div>

                {/* Input */}
                <div className="sticky bottom-8">
                    <div className="glass-panel border border-violet/20 bg-void/80 backdrop-blur-md p-1">
                        <div className="flex items-end gap-2">
                            <textarea
                                ref={inputRef}
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Ask about the research, architecture, or any project..."
                                rows={1}
                                className="flex-1 bg-transparent text-ethereal/80 placeholder-ethereal/20 font-mono text-sm px-4 py-3 resize-none focus:outline-none leading-relaxed"
                                style={{ minHeight: '48px', maxHeight: '160px' }}
                                onInput={(e) => {
                                    const t = e.currentTarget;
                                    t.style.height = 'auto';
                                    t.style.height = `${Math.min(t.scrollHeight, 160)}px`;
                                }}
                                disabled={loading}
                            />
                            <button
                                onClick={() => submit(input)}
                                disabled={!input.trim() || loading}
                                className="p-3 text-violet/60 hover:text-violet disabled:opacity-20 transition-colors flex-shrink-0"
                            >
                                <Send size={16} strokeWidth={1} />
                            </button>
                        </div>
                    </div>
                    <p className="text-[9px] font-mono text-ethereal/20 tracking-widest text-center mt-2 uppercase">
                        Enter to send · Shift+Enter for newline
                    </p>
                </div>

            </div>
        </main>
    );
}
