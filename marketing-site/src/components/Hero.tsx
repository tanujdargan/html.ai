"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import Carousel from "./Carousel";

export default function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center px-4 pt-32 pb-20">
      {/* Background gradient */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[800px] rounded-full bg-primary/20 blur-[120px]" />
        <div className="absolute top-1/3 left-1/4 w-[400px] h-[400px] rounded-full bg-blue-500/10 blur-[100px]" />
        <div className="absolute top-1/2 right-1/4 w-[300px] h-[300px] rounded-full bg-violet-500/10 blur-[80px]" />
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-5xl mx-auto text-center">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-8"
        >
          <Image
            src="/uofthacks-logo.svg"
            alt="UofTHacks"
            width={20}
            height={20}
          />
          <span className="text-sm text-muted-foreground">
            Born from UofT Hacks
          </span>
        </motion.div>

        {/* Main headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black tracking-tight mb-6"
        >
          <span className="gradient-text">Embedding Identity</span>
          <br />
          <span className="text-foreground inline-flex items-center">
            to C
            <span className="relative inline-block w-[0.85em] h-[0.85em] mx-[-0.05em]">
              <Image
                src="/html-ai-icon.png"
                alt="o"
                fill
                className="object-contain"
              />
            </span>
            mponents
          </span>
        </motion.h1>

        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10"
        >
          We help create dynamic experiences based on user&apos;s behavioral
          identity. Adaptive UI that responds to who your users truly are.
        </motion.p>

        {/* CTA Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <Link
            href="#get-started"
            className="inline-flex items-center gap-2 px-8 py-4 bg-primary text-primary-foreground font-semibold text-lg rounded-full hover:opacity-90 transition-all glow hover:scale-105"
          >
            Get Started
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 7l5 5m0 0l-5 5m5-5H6"
              />
            </svg>
          </Link>
        </motion.div>
      </div>

      {/* Carousel Section */}
      <motion.div
        id="demo"
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.5 }}
        className="relative z-10 w-full max-w-6xl mx-auto mt-20 scroll-mt-32"
      >
        <Carousel />
      </motion.div>
    </section>
  );
}
