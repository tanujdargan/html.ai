"use client";

import { motion, useInView } from "framer-motion";
import { useRef } from "react";

const useCases = [
  {
    id: 1,
    title: "Retail & E-commerce",
    category: "Industry",
    height: "h-80",
    gradient: "from-violet-500/20 to-purple-600/20",
  },
  {
    id: 2,
    title: "SaaS Platforms",
    category: "Industry",
    height: "h-72",
    gradient: "from-blue-500/20 to-cyan-500/20",
  },
  {
    id: 3,
    title: "News & Media",
    category: "Niche",
    height: "h-96",
    gradient: "from-amber-500/20 to-orange-500/20",
  },
  {
    id: 4,
    title: "Healthcare",
    category: "Industry",
    height: "h-64",
    gradient: "from-emerald-500/20 to-teal-500/20",
  },
  {
    id: 5,
    title: "Gen Z Users",
    category: "Demographic",
    height: "h-72",
    gradient: "from-pink-500/20 to-rose-500/20",
  },
  {
    id: 6,
    title: "Enterprise B2B",
    category: "Demographic",
    height: "h-64",
    gradient: "from-purple-500/20 to-fuchsia-500/20",
  },
];

export default function UseCases() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section className="relative py-32 px-4 scroll-mt-24" id="use-cases">
      {/* Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/2 left-1/4 w-[600px] h-[600px] rounded-full bg-primary/5 blur-[150px]" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] rounded-full bg-blue-500/5 blur-[100px]" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Section header */}
        <motion.div
          ref={ref}
          initial={{ opacity: 0, y: 40 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <h2 className="text-4xl sm:text-5xl md:text-6xl font-extrabold mb-6">
            <span className="gradient-text">Adapt for Anything</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Any niche, industry, demographic. Build experiences that resonate
            with every user segment.
          </p>
        </motion.div>

        {/* Masonry grid */}
        <div className="masonry-grid">
          {useCases.map((useCase, index) => (
            <motion.div
              key={useCase.id}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: index * 0.05 }}
              className="masonry-item"
            >
              <div
                className={`${useCase.height} rounded-2xl bg-gradient-to-br ${useCase.gradient} border border-border/50 p-6 flex flex-col justify-between hover:border-primary/50 transition-all cursor-pointer group overflow-hidden relative`}
              >
                {/* Placeholder for GIF/visual content */}
                <div className="flex-1 flex items-center justify-center">
                  <div className="w-full h-full rounded-xl bg-black/20 flex items-center justify-center">
                    <svg
                      className="w-12 h-12 text-white/30 group-hover:text-white/50 transition-colors"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1.5}
                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                  </div>
                </div>

                {/* Card content */}
                <div className="mt-4">
                  <span className="text-xs text-muted-foreground uppercase tracking-wider">
                    {useCase.category}
                  </span>
                  <h3 className="text-lg font-semibold mt-1 group-hover:text-primary transition-colors">
                    {useCase.title}
                  </h3>
                </div>

                {/* Hover overlay */}
                <div className="absolute inset-0 bg-primary/10 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
