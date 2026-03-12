import React from 'react';

interface EmotiveCoreProps {
    emotive: {
        curiosity: number;
        determination: number;
        frustration: number;
        calmness: number;
    };
}

const EmotiveCore: React.FC<EmotiveCoreProps> = ({ emotive }) => {
    return (
        <div className="p-4 space-y-8 glass border-t border-brass/10 border-l h-full">
            <div className="flex items-center justify-between border-b border-brass/10 pb-2">
                <h2 className="text-[10px] uppercase font-bold tracking-[0.2em] text-brass">Emotive Core</h2>
            </div>

            <div className="flex flex-col items-center justify-center space-y-12 py-10">
                {/* Curiosity: Brass Needle */}
                <div className="relative group">
                    <div className="text-[9px] uppercase mono text-brass mb-2 text-center">Curiosity</div>
                    <div className="w-32 h-1 bg-brass/20 rounded-full relative overflow-hidden">
                        <div
                            className="absolute h-full bg-brass brass-glow transition-all duration-300 ease-out"
                            style={{
                                width: '4px',
                                left: `${emotive.curiosity * 100}%`,
                                transform: `translateX(-50%) skewX(${(Math.random() - 0.5) * 20}deg)`
                            }}
                        />
                    </div>
                    <div className="absolute -inset-4 bg-brass/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-full -z-10 blur-xl" />
                </div>

                {/* Determination: Emerald Arc */}
                <div className="relative text-center">
                    <div className="text-[9px] uppercase mono text-forest-bright mb-4">Determination</div>
                    <div className="relative w-24 h-24">
                        <svg className="w-full h-full transform -rotate-90">
                            <circle
                                cx="48"
                                cy="48"
                                r="40"
                                stroke="currentColor"
                                strokeWidth="4"
                                fill="transparent"
                                className="text-forest/20"
                            />
                            <circle
                                cx="48"
                                cy="48"
                                r="40"
                                stroke="currentColor"
                                strokeWidth="4"
                                fill="transparent"
                                strokeDasharray={251.2}
                                strokeDashoffset={251.2 - (emotive.determination * 251.2)}
                                className="text-forest-bright transition-all duration-1000 ease-in-out"
                                style={{ filter: 'drop-shadow(0 0 4px var(--forest-bright))' }}
                            />
                        </svg>
                    </div>
                </div>

                {/* Frustration: Red Pulse */}
                <div className="relative group">
                    <div className="text-[9px] uppercase mono text-danger mb-2 text-center">Frustration</div>
                    <div
                        className={`w-12 h-12 rounded-full border-2 border-danger flex items-center justify-center transition-all ${emotive.frustration > 0.5 ? 'animate-ping' : ''}`}
                        style={{ opacity: 0.2 + (emotive.frustration * 0.8) }}
                    >
                        <div className="w-4 h-4 bg-danger rounded-full" />
                    </div>
                </div>

                {/* Calmness: Obsidian Base */}
                <div className="relative w-full pt-8 scale-x-150">
                    <div className="text-[9px] uppercase mono text-text-dim mb-2 text-center">Calmness</div>
                    <div className="h-8 w-full relative">
                        <div
                            className="absolute inset-0 bg-obsidian border-t border-brass/10 transition-all duration-[2000ms]"
                            style={{
                                opacity: 0.5 + (emotive.calmness * 0.5),
                                boxShadow: `0 -10px 20px rgba(0,0,0,${emotive.calmness})`
                            }}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default EmotiveCore;
