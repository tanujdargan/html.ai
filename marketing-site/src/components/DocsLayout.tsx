"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import Image from "next/image";
import { useState } from "react";
import { Menu, X, ChevronRight, Home, Book, Code, Layers, Server } from "lucide-react";
import { usePathname } from "next/navigation";

const menuItems = [
  {
    title: "Overview",
    href: "/docs",
    icon: Home,
  },
  {
    title: "Getting Started",
    href: "/docs/getting-started",
    icon: Book,
    items: [
      { name: "Installation", href: "/docs/getting-started#installation" },
      { name: "Quick Start", href: "/docs/getting-started#quick-start" },
      { name: "Configuration", href: "/docs/getting-started#configuration" },
    ],
  },
  {
    title: "Core Concepts",
    href: "/docs/core-concepts",
    icon: Layers,
    items: [
      { name: "Components", href: "/docs/core-concepts#components" },
      { name: "Data Attributes", href: "/docs/core-concepts#data-attributes" },
      { name: "Event Tracking", href: "/docs/core-concepts#event-tracking" },
    ],
  },
  {
    title: "API Reference",
    href: "/docs/api-reference",
    icon: Code,
    items: [
      { name: "SDK Methods", href: "/docs/api-reference#sdk-methods" },
      { name: "Auto-tracked Events", href: "/docs/api-reference#auto-tracked" },
    ],
  },
  {
    title: "Architecture",
    href: "/docs/architecture",
    icon: Server,
    items: [
      { name: "System Overview", href: "/docs/architecture#overview" },
      { name: "Services", href: "/docs/architecture#services" },
      { name: "Docker Setup", href: "/docs/architecture#docker" },
      { name: "Database", href: "/docs/architecture#database" },
    ],
  },
];

interface DocsLayoutProps {
  children: React.ReactNode;
  title: string;
  description: string;
}

export default function DocsLayout({ children, title, description }: DocsLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === "/docs") {
      return pathname === "/docs";
    }
    return pathname.startsWith(href);
  };

  return (
    <main className="relative min-h-screen">
      {/* Background gradient */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[800px] rounded-full bg-primary/10 blur-[120px]" />
        <div className="absolute bottom-0 right-0 w-[600px] h-[600px] rounded-full bg-emerald-500/5 blur-[100px]" />
      </div>

      {/* Header */}
      <header className="fixed top-0 inset-x-0 z-50 glass border-b border-border">
        <nav className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              type="button"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 hover:bg-white/10 rounded-lg transition-colors"
              aria-label="Toggle menu"
            >
              {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
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
            <span className="text-muted-foreground">/</span>
            <Link href="/docs" className="text-sm font-medium hover:text-primary transition-colors">
              Docs
            </Link>
          </div>
          <Link
            href="/"
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Back to Home
          </Link>
        </nav>
      </header>

      <div className="flex pt-16">
        {/* Sidebar - Desktop */}
        <aside className="hidden lg:block fixed top-16 left-0 z-40 h-[calc(100vh-4rem)] w-72 glass border-r border-border overflow-y-auto">
          <nav className="p-6 space-y-2">
            {menuItems.map((section) => {
              const Icon = section.icon;
              const active = isActive(section.href);
              
              return (
                <div key={section.title} className="mb-4">
                  <Link
                    href={section.href}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg font-medium transition-all ${
                      active 
                        ? "bg-primary/20 text-primary" 
                        : "text-foreground hover:bg-white/5"
                    }`}
                  >
                    <Icon size={18} />
                    {section.title}
                  </Link>
                  {section.items && active && (
                    <ul className="mt-2 ml-7 space-y-1 border-l border-border/50 pl-3">
                      {section.items.map((item) => (
                        <li key={item.name}>
                          <a
                            href={item.href}
                            className="flex items-center gap-2 px-2 py-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
                          >
                            <ChevronRight size={12} />
                            {item.name}
                          </a>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              );
            })}
          </nav>
        </aside>

        {/* Sidebar - Mobile */}
        <aside
          className={`lg:hidden fixed top-16 left-0 z-40 h-[calc(100vh-4rem)] w-72 glass border-r border-border overflow-y-auto transition-transform duration-300 ease-in-out ${
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          }`}
        >
          <nav className="p-6 space-y-2">
            {menuItems.map((section) => {
              const Icon = section.icon;
              const active = isActive(section.href);
              
              return (
                <div key={section.title} className="mb-4">
                  <Link
                    href={section.href}
                    onClick={() => setSidebarOpen(false)}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg font-medium transition-all ${
                      active 
                        ? "bg-primary/20 text-primary" 
                        : "text-foreground hover:bg-white/5"
                    }`}
                  >
                    <Icon size={18} />
                    {section.title}
                  </Link>
                  {section.items && (
                    <ul className="mt-2 ml-7 space-y-1 border-l border-border/50 pl-3">
                      {section.items.map((item) => (
                        <li key={item.name}>
                          <a
                            href={item.href}
                            onClick={() => setSidebarOpen(false)}
                            className="flex items-center gap-2 px-2 py-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
                          >
                            <ChevronRight size={12} />
                            {item.name}
                          </a>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              );
            })}
          </nav>
        </aside>

        {/* Overlay */}
        {sidebarOpen && (
          <div
            className="lg:hidden fixed inset-0 bg-black/50 z-30"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Content */}
        <div className="flex-1 lg:ml-72 relative z-10 min-h-screen">
          <div className="max-w-4xl mx-auto px-6 py-12">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
                {title}
              </h1>
              <p className="text-muted-foreground text-lg mb-12 leading-relaxed">
                {description}
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              {children}
            </motion.div>
          </div>
        </div>
      </div>
    </main>
  );
}
