"use client";

import DocsLayout from "@/components/DocsLayout";

export default function GettingStartedPage() {
  return (
    <DocsLayout
      title="Getting Started"
      description="Get up and running with html.ai in minutes."
    >
      {/* Installation */}
      <section id="installation" className="mb-16 scroll-mt-24">
        <h2 className="text-2xl font-semibold mb-6">Installation</h2>
        <p className="text-muted-foreground mb-6">
          Add the SDK with a single script tag:
        </p>
        <div className="glass rounded-xl p-5 overflow-x-auto border border-border/50">
          <pre className="text-sm font-mono">
            <code className="text-emerald-400">{`<script type="module" src="./sdk/src/AiOptimizeElement_v2.js"></script>`}</code>
          </pre>
        </div>
      </section>

      {/* Quick Start */}
      <section id="quick-start" className="mb-16 scroll-mt-24">
        <h2 className="text-2xl font-semibold mb-6">Quick Start</h2>

        <div className="space-y-6">
          <div className="glass rounded-xl p-5 border border-border/50">
            <div className="flex items-center gap-3 mb-3">
              <span className="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-emerald-500 text-primary-foreground text-sm flex items-center justify-center font-bold">1</span>
              <h3 className="font-medium">Get your API key</h3>
            </div>
            <p className="text-muted-foreground text-sm ml-10">
              Sign up at the dashboard to get your public key (<code className="bg-black/30 px-1 rounded text-xs">pk_*</code>).
            </p>
          </div>

          <div className="glass rounded-xl p-5 border border-border/50">
            <div className="flex items-center gap-3 mb-3">
              <span className="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-emerald-500 text-primary-foreground text-sm flex items-center justify-center font-bold">2</span>
              <h3 className="font-medium">Add the SDK script</h3>
            </div>
            <p className="text-muted-foreground text-sm ml-10">
              Include before <code className="bg-black/30 px-1 rounded text-xs">&lt;/body&gt;</code>. The SDK auto-initializes.
            </p>
          </div>

          <div className="glass rounded-xl p-5 border border-border/50">
            <div className="flex items-center gap-3 mb-3">
              <span className="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-emerald-500 text-primary-foreground text-sm flex items-center justify-center font-bold">3</span>
              <h3 className="font-medium">Wrap your components</h3>
            </div>
            <div className="ml-10 glass rounded-lg p-4 overflow-x-auto border border-border/30">
              <pre className="text-sm font-mono">
                <code className="text-emerald-400">{`<ai-opt experiment="hero">
  <h1>Welcome</h1>
  <button>Shop Now</button>
</ai-opt>`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Configuration */}
      <section id="configuration" className="scroll-mt-24">
        <h2 className="text-2xl font-semibold mb-6">Configuration</h2>
        
        <div className="glass rounded-xl overflow-hidden border border-border/50">
          <table className="w-full text-sm">
            <thead className="border-b border-border bg-white/5">
              <tr>
                <th className="text-left p-4 font-semibold">Attribute</th>
                <th className="text-left p-4 font-semibold">Description</th>
              </tr>
            </thead>
            <tbody>
              {[
                { attr: "experiment", desc: "Unique experiment/component identifier (required)" },
                { attr: "type=\"module\"", desc: "Required for ES module import" },
              ].map((row) => (
                <tr key={row.attr} className="border-b border-border/50 hover:bg-white/5">
                  <td className="p-4 font-mono text-primary">{row.attr}</td>
                  <td className="p-4 text-muted-foreground">{row.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </DocsLayout>
  );
}
