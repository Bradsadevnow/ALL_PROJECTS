import React from 'react';
import { ShieldAlert } from 'lucide-react';

interface ResourceGuardProps {
    tokens: {
        total_usage: number;
        threshold: number;
        hard_cap: number;
        remaining: number;
    };
}

const ResourceGuard: React.FC<ResourceGuardProps> = ({ tokens }) => {
    const percentage = (tokens.total_usage / tokens.hard_cap) * 100;
    const isApproaching = tokens.total_usage >= tokens.threshold;

    return (
        <div className="h-10 border-t border-brass/20 bg-obsidian/80 backdrop-blur-sm flex items-center px-6 justify-between">
            <div className="flex items-center space-x-4 flex-1">
                <span className="text-[9px] mono text-text-dim uppercase tracking-[0.2em]">Token Pressure</span>
                <div className="relative h-1.5 bg-obsidian border border-brass/20 flex-1 max-w-md">
                    <div
                        className={`h-full transition-all duration-500 ${isApproaching ? 'bg-brass brass-glow' : 'bg-forest'}`}
                        style={{ width: `${Math.min(100, percentage)}%` }}
                    />
                </div>
                <span className={`text-[10px] mono ${isApproaching ? 'text-brass font-bold' : 'text-text-dim'}`}>
                    {tokens.total_usage} / {tokens.hard_cap}
                </span>
            </div>

            <div className="flex items-center space-x-6 ml-8">
                {isApproaching && (
                    <div className="flex items-center space-x-2 text-brass animate-pulse">
                        <ShieldAlert size={12} />
                        <span className="text-[9px] mono uppercase font-bold">Consolidation Required</span>
                    </div>
                )}
                <div className="flex items-center space-x-2">
                    <span className="text-[9px] mono text-text-dim uppercase">Status:</span>
                    <span className="text-[9px] mono text-forest-bright uppercase font-bold crt-effect">Optimal</span>
                </div>
            </div>
        </div>
    );
};

export default ResourceGuard;
