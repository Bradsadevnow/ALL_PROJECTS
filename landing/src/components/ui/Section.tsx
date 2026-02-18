import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

interface SectionProps {
    children: React.ReactNode;
    className?: string;
    id?: string;
}

export const Section = ({ children, className = "", id }: SectionProps) => (
    <motion.section
        id={id}
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.7, ease: "easeOut" }}
        className={cn("py-24 px-6 max-w-6xl mx-auto relative", className)}
    >
        {children}
    </motion.section>
);
