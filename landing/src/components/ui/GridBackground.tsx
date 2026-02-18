
export const GridBackground = () => {
    return (
        <div className="fixed inset-0 pointer-events-none -z-10 bg-void overflow-hidden">
            {/* Background Image Asset */}
            <div
                className="absolute inset-0 z-0 opacity-20 bg-cover bg-center bg-no-repeat mix-blend-screen"
                style={{
                    backgroundImage: 'url(/img/Gemini_Generated_Image_yz08jeyz08jeyz08.png)',
                }}
            />

            {/* Base Gradient Overlay for readability */}
            <div className="absolute inset-0 bg-gradient-to-b from-void/80 via-void/50 to-void z-10" />

            {/* Moving Grid - Perspective */}
            <div
                className="absolute inset-0 opacity-20 z-20"
                style={{
                    backgroundImage: `linear-gradient(to right, #6B46C1 1px, transparent 1px),
                                      linear-gradient(to bottom, #6B46C1 1px, transparent 1px)`,
                    backgroundSize: '40px 40px',
                    transform: 'perspective(500px) rotateX(60deg) translateY(-100px) scale(2)',
                    transformOrigin: 'top center',
                    maskImage: 'linear-gradient(to bottom, transparent, black 40%, black 80%, transparent)'
                }}
            />

            {/* Ambient Glows */}
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-violet/10 blur-[120px] rounded-full mix-blend-screen z-20" />
            <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-ethereal/5 blur-[120px] rounded-full mix-blend-screen z-20" />
        </div>
    );
};
