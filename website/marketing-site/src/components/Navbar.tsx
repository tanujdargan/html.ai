"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import { Menu, X } from "lucide-react";

const navLinks = [
  { name: "Demo", href: "#demo" },
  { name: "Use Cases", href: "#use-cases" },
  { name: "Docs", href: "/docs" },
];

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <motion.header
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="fixed top-6 inset-x-0 z-50 mx-auto w-fit px-4"
    >
      <nav className="glass rounded-full px-5 py-2.5 flex items-center justify-center gap-6">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="relative w-7 h-7 overflow-hidden rounded-md">
            <Image
              src="/html-ai-icon.png"
              alt="html.ai logo"
              fill
              className="object-contain"
            />
          </div>
          <span className="font-semibold text-base tracking-tight group-hover:text-primary transition-colors">
            html.ai
          </span>
        </Link>

        {/* Divider */}
        <div className="hidden md:block w-px h-5 bg-border" />

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-5">
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

        {/* Mobile Menu Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-1.5 text-foreground"
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
          </div>
        </motion.div>
      )}
    </motion.header>
  );
}
