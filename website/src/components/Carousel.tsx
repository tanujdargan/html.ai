"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect, useCallback } from "react";
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
  const [isPaused, setIsPaused] = useState(false);

  const getSlideIndex = (offset: number) => {
    return (current + offset + slides.length) % slides.length;
  };

  const paginate = useCallback((newDirection: number) => {
    setDirection(newDirection);
    setCurrent((prev) => (prev + newDirection + slides.length) % slides.length);
  }, []);

  // Auto-rotate every 4 seconds (clockwise)
  useEffect(() => {
    if (isPaused) return;
    const interval = setInterval(() => {
      paginate(-1);
    }, 4000);
    return () => clearInterval(interval);
  }, [isPaused, paginate]);

  return (
    <div 
      className="relative py-8"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      {/* Cards container */}
      <div className="flex items-center justify-center gap-4 lg:gap-8 px-4">
        {/* Left card */}
        <AnimatePresence mode="popLayout">
          <motion.div
            key={`left-${getSlideIndex(-1)}`}
            initial={{ opacity: 0, scale: 0.7, x: -50 }}
            animate={{ opacity: 0.5, scale: 0.85, x: 0 }}
            exit={{ opacity: 0, scale: 0.7, x: -50 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="hidden md:flex w-40 lg:w-56 flex-shrink-0"
          >
            <div className="glass rounded-2xl p-4 lg:p-5 aspect-[4/3] w-full flex flex-col items-center justify-center text-center">
              <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center mb-2">
                <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </div>
              <h4 className="text-xs lg:text-sm font-medium mb-1 line-clamp-1">{slides[getSlideIndex(-1)].title}</h4>
              <p className="text-xs text-muted-foreground line-clamp-2 hidden lg:block">{slides[getSlideIndex(-1)].description}</p>
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Center card */}
        <AnimatePresence mode="wait">
          <motion.div
            key={`center-${current}`}
            initial={{ opacity: 0, scale: 0.9, x: direction > 0 ? 100 : -100 }}
            animate={{ opacity: 1, scale: 1, x: 0 }}
            exit={{ opacity: 0, scale: 0.9, x: direction > 0 ? -100 : 100 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="w-full max-w-sm lg:max-w-md flex-shrink-0"
          >
            <a
              href={slides[current].link}
              target="_blank"
              rel="noopener noreferrer"
              className="block glass rounded-2xl p-5 lg:p-6 aspect-[4/3] w-full flex flex-col items-center justify-center text-center border-2 border-primary/30 hover:border-primary/60 transition-all group cursor-pointer"
            >
              <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center mb-3 group-hover:bg-primary/30 transition-colors">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </div>
              <h3 className="text-lg lg:text-xl font-semibold mb-2 gradient-text">{slides[current].title}</h3>
              <p className="text-muted-foreground text-sm">{slides[current].description}</p>
              <span className="mt-3 text-xs text-primary group-hover:underline">Click to open demo →</span>
            </a>
          </motion.div>
        </AnimatePresence>

        {/* Right card */}
        <AnimatePresence mode="popLayout">
          <motion.div
            key={`right-${getSlideIndex(1)}`}
            initial={{ opacity: 0, scale: 0.7, x: 50 }}
            animate={{ opacity: 0.5, scale: 0.85, x: 0 }}
            exit={{ opacity: 0, scale: 0.7, x: 50 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="hidden md:flex w-40 lg:w-56 flex-shrink-0"
          >
            <div className="glass rounded-2xl p-4 lg:p-5 aspect-[4/3] w-full flex flex-col items-center justify-center text-center">
              <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center mb-2">
                <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </div>
              <h4 className="text-xs lg:text-sm font-medium mb-1 line-clamp-1">{slides[getSlideIndex(1)].title}</h4>
              <p className="text-xs text-muted-foreground line-clamp-2 hidden lg:block">{slides[getSlideIndex(1)].description}</p>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Navigation - arrows and dots */}
      <div className="flex items-center justify-center gap-4 mt-6">
        <button
          onClick={() => paginate(-1)}
          className="p-2 rounded-full glass hover:bg-white/10 transition-colors"
          aria-label="Previous slide"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>

        {/* Dots indicator */}
        <div className="flex gap-2">
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

        <button
          onClick={() => paginate(1)}
          className="p-2 rounded-full glass hover:bg-white/10 transition-colors"
          aria-label="Next slide"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
