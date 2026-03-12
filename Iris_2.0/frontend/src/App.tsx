import React, { useState, useEffect } from 'react';
import EpochPulse from './components/EpochPulse';
import CognitiveWorkspace from './components/CognitiveWorkspace';
import ResourceGuard from './components/ResourceGuard';
import EmotiveCore from './components/EmotiveCore';

const App: React.FC = () => {
    const [history, setHistory] = useState<any>({ stm: [], ledger: [] });
    const [status, setStatus] = useState<any>({
        tokens: { total_usage: 0, threshold: 240000, hard_cap: 250000 },
        runtime_state: 'IDLE',
        emotive: { curiosity: 0.5, determination: 0.5, frustration: 0.1, calmness: 0.9 },
        pressure: 0
    });
    const [dream, setDream] = useState<string>('');

    const fetchState = async () => {
        try {
            const [histRes, statRes, dreamRes] = await Promise.all([
                fetch('/api/history'),
                fetch('/api/status'),
                fetch('/api/dream')
            ]);

            if (histRes.ok) setHistory(await histRes.json());
            if (statRes.ok) setStatus(await statRes.json());
            if (dreamRes.ok) {
                const data = await dreamRes.json();
                setDream(data.dream);
            }
        } catch (e) {
            console.error('Failed to fetch state', e);
        }
    };

    const triggerSleep = async () => {
        if (!confirm("Initiate Sleep Cycle (Consolidation)? This will reset current context.")) return;
        try {
            const resp = await fetch('/management/sleep', { method: 'POST' });
            if (resp.ok) {
                alert("Sleep Cycle complete. Identity re-anchored.");
                fetchState();
            }
        } catch (e) {
            console.error('Sleep Cycle failed', e);
        }
    };

    useEffect(() => {
        fetchState();
        const interval = setInterval(fetchState, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex flex-col h-screen bg-obsidian text-text-main overflow-hidden">
            {/* Header */}
            <header className="flex items-center justify-between px-6 py-3 border-b border-brass/20 glass h-14">
                <div className="flex items-center space-x-4">
                    <h1 className="text-brass text-xl font-bold tracking-tighter uppercase italic">
                        IRIS <span className="text-text-dim text-xs ml-2 font-normal not-italic">Thiccadome Console v1.0.0</span>
                    </h1>
                </div>
                <div className="flex items-center space-x-6">
                    {status.pressure > 0.5 && (
                        <button
                            onClick={triggerSleep}
                            className="text-[10px] bg-brass/10 border border-brass/30 text-brass px-3 py-1 rounded hover:bg-brass/20 transition-all uppercase tracking-widest animate-pulse"
                        >
                            Initiate Sleep Cycle
                        </button>
                    )}
                    <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${status.runtime_state === 'IDLE' ? 'bg-forest' : 'bg-brass animate-pulse'}`} />
                        <span className="text-[10px] text-text-dim uppercase tracking-widest mono">{status.runtime_state}</span>
                    </div>
                </div>
            </header>

            {/* Main Content Area */}
            <div className="flex-1 flex overflow-hidden">
                {/* Left Sidebar: Epoch Pulse */}
                <div className="w-64 border-r border-brass/10 overflow-y-auto bg-obsidian/50">
                    <EpochPulse ledger={history.ledger} />
                </div>

                {/* Center Stage: Cognitive Workspace */}
                <div className="flex-1 flex flex-col min-w-0 bg-[#080808]">
                    <CognitiveWorkspace
                        history={history.stm}
                        onMessageSent={fetchState}
                        dream={dream}
                    />
                </div>

                {/* Right Sidebar: Emotive Core */}
                <div className="w-64 border-l border-brass/10 overflow-y-auto bg-obsidian/50">
                    <EmotiveCore emotive={status.emotive} />
                </div>
            </div>

            {/* Bottom Bar: Resource Guard */}
            <ResourceGuard tokens={status.tokens} />
        </div>
    );
};

export default App;
