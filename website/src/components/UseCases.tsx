"use client";

import { motion, useInView } from "framer-motion";
import { useRef } from "react";

const useCases = [
  {
    id: 1,
    title: "Hyper-Personalization",
    subtitle: "The \"Segment of One\"",
    description: "Optimize for individuals, not averages. The engine maintains a profile for each user. If they prefer dark mode, high-density data, and technical jargon, the AI generates that specific UI every visit.",
    highlight: "Maximize conversion probability for every single session dynamically.",
    height: "h-auto",
    gradient: "from-violet-500/20 to-purple-600/20",
  },
  {
    id: 2,
    title: "Context-Aware Adaptation",
    subtitle: "Beyond On-Site Behavior",
    description: "Expand inputs to include environmental context. UI changes based on time (\"Late night snack?\" vs \"Lunch special\"), location, and user preferences for ambience or places.",
    highlight: "Dynamic SERP alignment rewrites H1s to match search intent perfectly.",
    height: "h-auto",
    gradient: "from-blue-500/20 to-cyan-500/20",
  },
  {
    id: 3,
    title: "Rage Click Detection",
    subtitle: "Frustration Response",
    description: "Detects rage clicking or rapid scrolling as signs of frustration. Instead of just trying a new design, it triggers \"simplification mode\" with minimal UI, removed distractions, and a clear help button.",
    highlight: "Turn frustrated users into converted customers.",
    height: "h-auto",
    gradient: "from-amber-500/20 to-orange-500/20",
  },
  {
    id: 4,
    title: "Cross-Site Federated Learning",
    subtitle: "Shared Intelligence",
    description: "Deploy across multiple websites to learn universal truths. If \"Green Buttons\" perform poorly across fashion sites this week, preemptively stop suggesting them for new clients.",
    highlight: "Jump-start optimization for new clients in the same vertical.",
    height: "h-auto",
    gradient: "from-emerald-500/20 to-teal-500/20",
  },
  {
    id: 5,
    title: "Framework Agnostic",
    subtitle: "Works Everywhere",
    description: "Integrate with any frontend: React, Vue, Angular, Swift, Flutter, or vanilla HTML. Our SDK adapts to your stack, not the other way around.",
    highlight: "One platform, every framework.",
    height: "h-auto",
    gradient: "from-pink-500/20 to-rose-500/20",
  },
  {
    id: 6,
    title: "Real-Time Intent Matching",
    subtitle: "Search Query Alignment",
    description: "When a user lands via \"durable hiking boots\", the engine instantly rewrites headlines and descriptions to emphasize durability and hiking, matching intent perfectly.",
    highlight: "Convert searchers by speaking their language.",
    height: "h-auto",
    gradient: "from-purple-500/20 to-fuchsia-500/20",
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

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
            <span className="gradient-text">Beyond A/B Testing</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Stop optimizing for the average user. Our AI creates a unique experience
            for every individual, adapting in real-time to context, intent, and behavior.
          </p>
        </motion.div>

        {/* Grid */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          variants={containerVariants}
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
        >
          {useCases.map((useCase, index) => (
            <motion.div
              key={useCase.id}
              variants={{
                hidden: {
                  opacity: 0,
                  y: 40,
                  scale: 0.95,
                },
                visible: {
                  opacity: 1,
                  y: 0,
                  scale: 1,
                  transition: {
                    type: "spring",
                    stiffness: 100,
                    damping: 15,
                  },
                },
              }}
              whileHover={{
                scale: 1.02,
                y: -4,
                transition: { type: "spring", stiffness: 400, damping: 20 }
              }}
            >
              <div
                className={`${useCase.height} rounded-2xl bg-gradient-to-br ${useCase.gradient} border border-border/50 p-6 flex flex-col hover:border-primary/50 transition-all cursor-pointer group overflow-hidden relative`}
              >
                {/* Card content */}
                <div>
                  <span className="text-xs text-primary uppercase tracking-wider font-medium">
                    {useCase.subtitle}
                  </span>
                  <h3 className="text-xl font-semibold mt-2 group-hover:text-primary transition-colors">
                    {useCase.title}
                  </h3>
                  <p className="text-sm text-muted-foreground mt-3 leading-relaxed">
                    {useCase.description}
                  </p>
                  <p className="text-sm text-foreground mt-4 font-medium border-l-2 border-primary pl-3">
                    {useCase.highlight}
                  </p>
                </div>

                {/* Hover overlay */}
                <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
