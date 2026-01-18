"use client";

import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { X, Check, Minus } from "lucide-react";

const comparisonData = {
  left: {
    title: "Static Personalization",
    subtitle: "Rule-based systems",
    cons: [
      "Manual segment creation",
      "Stale user profiles",
      "Limited behavioral signals",
      "One-size-fits-all fallback",
      "Complex integration",
      "Slow iteration cycles",
    ],
  },
  center: {
    title: "html.ai",
    subtitle: "Identity-first approach",
    pros: [
      "Auto-learning identity models",
      "Real-time behavioral adaptation",
      "Multi-signal intelligence",
      "Graceful degradation",
      "Drop-in integration",
      "Instant experimentation",
    ],
  },
  right: {
    title: "A/B Testing Platforms",
    subtitle: "Experiment-heavy approach",
    cons: [
      "Requires statistical significance",
      "Binary test outcomes",
      "No individual personalization",
      "High traffic requirements",
      "Manual hypothesis creation",
      "Delayed insights",
    ],
  },
};

export default function Comparison() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section className="relative py-32 px-4" id="comparison">
      {/* Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] rounded-full bg-primary/5 blur-[200px]" />
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
            Identity is Dynamic,
            <br />
            <span className="gradient-text">Adapt Experiences</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Stop treating users as static segments. Embrace continuous identity
            signals.
          </p>
        </motion.div>

        {/* Three column comparison */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-4">
          {/* Left card - Static Personalization */}
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="rounded-3xl bg-card border border-border p-8 relative overflow-hidden"
          >

            <div className="mb-8">
              <h3 className="text-2xl font-semibold mb-2">
                {comparisonData.left.title}
              </h3>
              <p className="text-muted-foreground">
                {comparisonData.left.subtitle}
              </p>
            </div>

            <ul className="space-y-4">
              {comparisonData.left.cons.map((con, index) => (
                <li key={index} className="flex items-start gap-3">
                  <div className="mt-0.5 p-1 rounded-full bg-red-500/10">
                    <X className="w-4 h-4 text-red-400" />
                  </div>
                  <span className="text-muted-foreground">{con}</span>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Center card - html.ai (highlighted) */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="rounded-3xl bg-gradient-to-b from-primary/10 to-card border-2 border-primary p-8 relative overflow-hidden lg:scale-105 lg:-my-4 shadow-2xl shadow-primary/20"
          >

            <div className="mb-8">
              <h3 className="text-2xl font-semibold mb-2 gradient-text">
                {comparisonData.center.title}
              </h3>
              <p className="text-muted-foreground">
                {comparisonData.center.subtitle}
              </p>
            </div>

            <ul className="space-y-4">
              {comparisonData.center.pros.map((pro, index) => (
                <li key={index} className="flex items-start gap-3">
                  <div className="mt-0.5 p-1 rounded-full bg-primary/20">
                    <Check className="w-4 h-4 text-primary" />
                  </div>
                  <span className="text-foreground font-medium">{pro}</span>
                </li>
              ))}
            </ul>

            {/* CTA */}
            <div className="mt-8 pt-6 border-t border-border">
              <a
                href="#get-started"
                className="block w-full py-3 px-6 bg-primary text-primary-foreground text-center font-semibold rounded-full hover:opacity-90 transition-opacity"
              >
                Start Building
              </a>
            </div>
          </motion.div>

          {/* Right card - A/B Testing */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="rounded-3xl bg-card border border-border p-8 relative overflow-hidden"
          >

            <div className="mb-8">
              <h3 className="text-2xl font-semibold mb-2">
                {comparisonData.right.title}
              </h3>
              <p className="text-muted-foreground">
                {comparisonData.right.subtitle}
              </p>
            </div>

            <ul className="space-y-4">
              {comparisonData.right.cons.map((con, index) => (
                <li key={index} className="flex items-start gap-3">
                  <div className="mt-0.5 p-1 rounded-full bg-yellow-500/10">
                    <Minus className="w-4 h-4 text-yellow-400" />
                  </div>
                  <span className="text-muted-foreground">{con}</span>
                </li>
              ))}
            </ul>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
