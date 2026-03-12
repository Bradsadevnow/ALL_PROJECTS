import React from 'react';
import { Shield, Sparkles } from 'lucide-react';
import EmotiveCore from './EmotiveCore';

interface MindMonitorProps {
    emotive: any;
    identity: string;
    dream: string;
}

const MindMonitor: React.FC<MindMonitorProps> = ({ emotive, identity, dream }) => {
    return (
        <div className="flex flex-col h-full bg-obsidian/30 border-l border-brass/10 overflow-hidden terminal-text">
            {/* Emotive Core Section */}
            <div className="p-4 border-b border-brass/5">
                <h3 className="text-[10px] text-brass/60 mono uppercase tracking-[0.3em] mb-4">Internal Stimuli</h3>
                <EmotiveCore emotive={emotive} />
            </div>

            {/* Identity Context Section */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-brass/10">
                <div className="flex items-center space-x-2 text-brass/80">
                    <Shield size={14} />
                    <h3 className="text-[10px] mono uppercase tracking-[0.3em]">Identity Contract</h3>
                </div>
                <div className="text-[11px] text-text-dim/80 leading-relaxed whitespace-pre-wrap bg-brass/5 p-3 rounded border border-brass/10 border-dashed">
                    {identity || "Synchronizing identity..."}
                </div>

                {/* Dream Fragment Section */}
                <div className="pt-4 border-t border-brass/5 space-y-3">
                    <div className="flex items-center space-x-2 text-brass/80">
                        <Sparkles size={14} />
                        <h3 className="text-[10px] mono uppercase tracking-[0.3em]">Subconscious</h3>
                    </div>
                    <div className="p-3 bg-forest/5 border border-forest/20 rounded italic text-[11px] text-forest-bright/80 leading-relaxed group">
                        <span className="text-[9px] uppercase font-bold tracking-widest block mb-1 opacity-40">Residual Trace</span>
                        "{dream || "No current residuals."}"
                    </div>
                </div>
            </div>

            <div className="p-3 bg-brass/5 border-t border-brass/10 border-dashed">
                <p className="text-[9px] text-text-dim mono uppercase tracking-tighter opacity-50">
          // Glass Box Monitor v1.2: Persistent Mind-State Feed.
                    Stability: NOMINAL.
                </p>
            </div>
        </div>
    );
};

export default MindMonitor;
