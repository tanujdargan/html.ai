"use client";

import DocsLayout from "@/components/DocsLayout";

export default function CoreConceptsPage() {
  return (
    <DocsLayout
      title="Core Concepts"
      description="Components, data attributes, and behavioral tracking fundamentals."
    >
      {/* Components */}
      <section id="components" className="mb-16 scroll-mt-24">
        <h2 className="text-2xl font-semibold mb-6">Components</h2>
        <p className="text-muted-foreground mb-6 leading-relaxed">
          Wrap content to personalize with the <code className="bg-black/30 px-1.5 py-0.5 rounded text-xs font-mono text-primary">&lt;ai-optimize&gt;</code> element:
        </p>

        <div className="glass rounded-xl p-5 overflow-x-auto border border-border/50 mb-6">
          <pre className="text-sm font-mono">
            <code className="text-emerald-400">{`<ai-optimize component-id="hero-section">
  <h1 data-ai="headline">Welcome</h1>
  <p data-ai="subheadline">Find the best products</p>
  <button data-ai="cta">Shop Now</button>
</ai-optimize>`}</code>
          </pre>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="glass rounded-lg p-4 border border-border/50">
            <code className="text-primary text-sm">component-id</code>
            <p className="text-xs text-muted-foreground mt-1">Unique identifier for tracking and analytics</p>
          </div>
          <div className="glass rounded-lg p-4 border border-border/50">
            <code className="text-primary text-sm">data-ai</code>
            <p className="text-xs text-muted-foreground mt-1">Marks elements for AI content optimization</p>
          </div>
        </div>
      </section>

      {/* Data Attributes */}
      <section id="data-attributes" className="mb-16 scroll-mt-24">
        <h2 className="text-2xl font-semibold mb-6">Data Attributes</h2>

        <div className="glass rounded-xl overflow-hidden border border-border/50 mb-8">
          <table className="w-full text-sm">
            <thead className="border-b border-border bg-white/5">
              <tr>
                <th className="text-left p-4 font-semibold">Attribute</th>
                <th className="text-left p-4 font-semibold">Description</th>
              </tr>
            </thead>
            <tbody>
              {[
                { attr: 'data-ai="headline"', desc: "Main headline to optimize" },
                { attr: 'data-ai="subheadline"', desc: "Secondary text to optimize" },
                { attr: 'data-ai="cta"', desc: "Call-to-action (triggers conversion)" },
                { attr: "data-track-hover", desc: "Track hover duration" },
                { attr: "data-component-id", desc: "Associate with a component" },
              ].map((row) => (
                <tr key={row.attr} className="border-b border-border/50 hover:bg-white/5">
                  <td className="p-4 font-mono text-primary">{row.attr}</td>
                  <td className="p-4 text-muted-foreground">{row.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h3 className="text-lg font-medium mb-4">Identity States</h3>
        <p className="text-muted-foreground mb-4 text-sm">
          Users are categorized into behavioral states based on their interactions:
        </p>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {[
            { state: "confident", desc: "Quick decisions" },
            { state: "exploratory", desc: "Browsing behavior" },
            { state: "cautious", desc: "Hesitation patterns" },
            { state: "impulse_buyer", desc: "Fast engagement" },
            { state: "comparison_focused", desc: "Deep analysis" },
            { state: "overwhelmed", desc: "Frustration signals" },
          ].map((item) => (
            <div key={item.state} className="glass rounded-lg p-3 border border-border/50">
              <code className="text-primary text-xs font-mono">{item.state}</code>
              <p className="text-xs text-muted-foreground mt-0.5">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Event Tracking */}
      <section id="event-tracking" className="scroll-mt-24">
        <h2 className="text-2xl font-semibold mb-6">Event Tracking</h2>
        <p className="text-muted-foreground mb-6">
          Track custom events to improve personalization:
        </p>

        <div className="glass rounded-xl p-5 overflow-x-auto border border-border/50">
          <pre className="text-sm font-mono">
            <code className="text-emerald-400">{`// Track custom event
HtmlAI.track('product_viewed', 'product-123', {
  name: 'Running Shoes',
  price: 99.99
});

// Get user identity
const user = HtmlAI.getUser();`}</code>
          </pre>
        </div>
      </section>
    </DocsLayout>
  );
}
