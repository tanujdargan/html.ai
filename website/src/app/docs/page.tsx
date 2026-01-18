"use client";

import DocsLayout from "@/components/DocsLayout";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function DocsPage() {
  return (
    <DocsLayout
      title="Documentation"
      description="Everything you need to integrate html.ai."
    >
      {/* Introduction */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold mb-4">Introduction</h2>
        <p className="text-muted-foreground mb-4 leading-relaxed">
          html.ai provides AI-powered UI personalization for websites. The SDK tracks user behavior, 
          identifies behavioral patterns, and dynamically optimizes content to match each user's intent.
        </p>
        <p className="text-muted-foreground mb-6 leading-relaxed">
          <strong className="text-foreground">This documentation is organized into four sections:</strong>
        </p>
        <ul className="space-y-2 text-sm text-muted-foreground mb-6">
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-2"></span>
            <span><Link href="/docs/getting-started" className="text-foreground underline hover:text-primary transition-colors">Getting Started</Link> — Installation, setup, and configuration</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-2"></span>
            <span><Link href="/docs/core-concepts" className="text-foreground underline hover:text-primary transition-colors">Core Concepts</Link> — How components, attributes, and tracking work</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-400 mt-2"></span>
            <span><Link href="/docs/api-reference" className="text-foreground underline hover:text-primary transition-colors">API Reference</Link> — SDK methods and events (REST API docs available on the server)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-2"></span>
            <span><Link href="/docs/architecture" className="text-foreground underline hover:text-primary transition-colors">Architecture</Link> — System design, services, and Docker deployment</span>
          </li>
        </ul>
      </section>

      {/* Quick Start */}
      <section>
        <h2 className="text-xl font-semibold mb-4">Quick Start</h2>
        
        <div className="glass rounded-xl p-5 overflow-x-auto border border-border/50 mb-4">
          <pre className="text-sm font-mono">
            <code className="text-emerald-400">{`<!-- 1. Add SDK -->
<script type="module" src="./sdk/src/AiOptimizeElement_v2.js"></script>

<!-- 2. Wrap components -->
<ai-opt experiment="hero">
  <h1>Welcome</h1>
  <button>Shop Now</button>
</ai-opt>`}</code>
          </pre>
        </div>

        <div className="flex gap-3">
          <Link
            href="/docs/getting-started"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors"
          >
            Full Guide <ArrowRight size={14} />
          </Link>
          <Link
            href="/docs/architecture"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-border text-sm hover:bg-white/5 transition-colors"
          >
            View Architecture
          </Link>
        </div>
      </section>
    </DocsLayout>
  );
}
