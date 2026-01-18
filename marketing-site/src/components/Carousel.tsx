"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

const slides = [
  {
    id: 1,
    title: "Business A - Shoes",
    description: "E-commerce demo showcasing personalized shoe recommendations",
    link: "http://localhost:8082/demo-business-a.html",
  },
  {
    id: 2,
    title: "Business B - Clothes",
    description: "Fashion store demo with adaptive clothing suggestions",
    link: "http://localhost:8082/demo-business-b.html",
  },
  {
    id: 3,
    title: "Admin Dashboard",
    description: "Manage and monitor your html.ai integrations",
    link: "http://localhost:8081/",
  },
];

export default function Carousel() {
  const [current, setCurrent] = useState(0);
  const [direction, setDirection] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setDirection(1);
      setCurrent((prev) => (prev + 1) % slides.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  const slideVariants = {
    enter: (direction: number) => ({
      x: direction > 0 ? 1000 : -1000,
      opacity: 0,
    }),
    center: {
      zIndex: 1,
      x: 0,
      opacity: 1,
    },
    exit: (direction: number) => ({
      zIndex: 0,
      x: direction < 0 ? 1000 : -1000,
      opacity: 0,
    }),
  };

  const paginate = (newDirection: number) => {
    setDirection(newDirection);
    setCurrent(
      (prev) => (prev + newDirection + slides.length) % slides.length
    );
  };

  return (
    <div className="relative">
      {/* Main carousel container */}
      <div className="relative overflow-hidden rounded-2xl glass">
        <div className="aspect-video relative">
          <AnimatePresence initial={false} custom={direction}>
            <motion.div
              key={current}
              custom={direction}
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{
                x: { type: "spring", stiffness: 300, damping: 30 },
                opacity: { duration: 0.2 },
              }}
              className="absolute inset-0 flex flex-col items-center justify-center p-8"
            >
              {/* Demo Link */}
              <a
                href={slides[current].link}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full max-w-4xl aspect-video rounded-xl bg-gradient-to-br from-primary/20 via-secondary to-primary/10 border border-border flex items-center justify-center mb-6 hover:border-primary/50 transition-colors cursor-pointer group"
              >
                <div className="text-center p-8">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/20 flex items-center justify-center group-hover:bg-primary/30 transition-colors">
                    <svg
                      className="w-8 h-8 text-primary"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                      />
                    </svg>
                  </div>
                  <p className="text-muted-foreground text-sm group-hover:text-foreground transition-colors">
                    Click to open demo
                  </p>
                </div>
              </a>

              {/* Slide info */}
              <h3 className="text-2xl font-semibold mb-2">
                {slides[current].title}
              </h3>
              <p className="text-muted-foreground">
                {slides[current].description}
              </p>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>

      {/* Navigation arrows */}
      <button
        onClick={() => paginate(-1)}
        className="absolute left-4 top-1/2 -translate-y-1/2 p-3 rounded-full glass hover:bg-white/10 transition-colors"
        aria-label="Previous slide"
      >
        <ChevronLeft className="w-6 h-6" />
      </button>
      <button
        onClick={() => paginate(1)}
        className="absolute right-4 top-1/2 -translate-y-1/2 p-3 rounded-full glass hover:bg-white/10 transition-colors"
        aria-label="Next slide"
      >
        <ChevronRight className="w-6 h-6" />
      </button>

      {/* Dots indicator */}
      <div className="flex justify-center gap-2 mt-6">
        {slides.map((_, index) => (
          <button
            key={index}
            onClick={() => {
              setDirection(index > current ? 1 : -1);
              setCurrent(index);
            }}
            className={`w-2 h-2 rounded-full transition-all ${
              index === current
                ? "w-8 bg-primary"
                : "bg-muted-foreground/30 hover:bg-muted-foreground/50"
            }`}
            aria-label={`Go to slide ${index + 1}`}
          />
        ))}
      </div>
    </div>
  );
}
