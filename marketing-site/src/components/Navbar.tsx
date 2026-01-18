"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import { Menu, X } from "lucide-react";

const navLinks = [
  { name: "Demo", href: "#demo" },
  { name: "Use Cases", href: "#use-cases" },
  { name: "FAQ", href: "#faq" },
  { name: "Docs", href: "#docs" },
];

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <motion.header
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="fixed top-6 inset-x-0 z-50 mx-auto w-full max-w-4xl px-4"
    >
      <nav className="glass rounded-full px-6 py-3 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="relative w-8 h-8 overflow-hidden rounded-lg">
            <Image
              src="/html-ai-icon.png"
              alt="html.ai logo"
              fill
              className="object-contain"
            />
          </div>
          <span className="font-semibold text-lg tracking-tight group-hover:text-primary transition-colors">
            html.ai
          </span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              href={link.href}
              className="text-sm text-muted-foreground hover:text-foreground transition-colors relative group"
            >
              {link.name}
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-primary transition-all group-hover:w-full" />
            </Link>
          ))}
        </div>

        {/* CTA Button */}
        <Link
          href="#get-started"
          className="hidden md:block px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-full hover:opacity-90 transition-opacity"
        >
          Get Started
        </Link>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 text-foreground"
          aria-label="Toggle menu"
        >
          {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </nav>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="md:hidden glass rounded-3xl mt-4 p-6"
        >
          <div className="flex flex-col gap-4">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className="text-foreground hover:text-primary transition-colors py-2"
              >
                {link.name}
              </Link>
            ))}
            <Link
              href="#get-started"
              onClick={() => setMobileMenuOpen(false)}
              className="mt-2 px-4 py-3 bg-primary text-primary-foreground text-center font-medium rounded-full hover:opacity-90 transition-opacity"
            >
              Get Started
            </Link>
          </div>
        </motion.div>
      )}
    </motion.header>
  );
}
