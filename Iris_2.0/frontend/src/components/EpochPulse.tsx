import React from 'react';
import { Activity } from 'lucide-react';

interface EpochPulseProps {
    ledger: any[];
}

const EpochPulse: React.FC<EpochPulseProps> = ({ ledger }) => {
    // Group ledger events by epoch_id for cleaner pulse
    const events = [...ledger].reverse();

    return (
        <div className="p-4 flex flex-col space-y-4">
            <div className="flex items-center space-x-2 mb-4 border-b border-brass/10 pb-2">
                <Activity size={14} className="text-brass" />
                <h2 className="text-[10px] uppercase font-bold tracking-[0.2em] text-brass">Event Ledger</h2>
            </div>

            <div className="space-y-3">
                {events.map((evt, idx) => (
                    <div key={idx} className="flex flex-col space-y-1 p-2 border-l border-brass/20 bg-brass/5 hover:bg-brass/10 transition-colors">
                        <div className="flex justify-between items-center">
                            <span className="text-[9px] text-brass mono uppercase tracking-tighter">
                                {evt.epoch_id.slice(0, 8)}...
                            </span>
                            <div className={`w-1.5 h-1.5 rounded-full ${evt.event_type === 'EpochCommitted' ? 'status-glow-committed' :
                                    evt.event_type === 'EpochAborted' ? 'status-glow-aborted' : 'bg-brass'
                                }`} />
                        </div>
                        <div className="text-[10px] text-text-dim mono truncate">
                            {evt.event_type}
                        </div>
                        {evt.payload?.user_input && (
                            <div className="text-[9px] text-forest-bright mono truncate italic opacity-60">
                                &gt; {evt.payload.user_input}
                            </div>
                        )}
                    </div>
                ))}

                {events.length === 0 && (
                    <div className="text-[10px] text-text-dim text-center py-8 italic opacity-50 mono">
                        Waiting for input...
                    </div>
                )}
            </div>
        </div>
    );
};

export default EpochPulse;
