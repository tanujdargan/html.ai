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
          Wrap content to personalize with the <code className="bg-black/30 px-1.5 py-0.5 rounded text-xs font-mono text-primary">&lt;ai-opt&gt;</code> element:
        </p>

        <div className="glass rounded-xl p-5 overflow-x-auto border border-border/50 mb-6">
          <pre className="text-sm font-mono">
            <code className="text-emerald-400">{`<ai-opt experiment="hero-block" component-id="1">
  <div class="hero">
    <h2>Comfort Runner Shoes</h2>
    <p>Ultra-light running shoes designed for all-day comfort.</p>
    <button>Shop Now</button>
  </div>
</ai-opt>`}</code>
          </pre>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="glass rounded-lg p-4 border border-border/50">
            <code className="text-primary text-sm">experiment</code>
            <p className="text-xs text-muted-foreground mt-1">Unique name for the experiment</p>
          </div>
          <div className="glass rounded-lg p-4 border border-border/50">
            <code className="text-primary text-sm">component-id</code>
            <p className="text-xs text-muted-foreground mt-1">ID used to link with reward-button</p>
          </div>
        </div>
      </section>

      {/* Reward Button */}
      <section id="reward-button" className="mb-16 scroll-mt-24">
        <h2 className="text-2xl font-semibold mb-6">Reward Button</h2>
        <p className="text-muted-foreground mb-6 leading-relaxed">
          Use <code className="bg-black/30 px-1.5 py-0.5 rounded text-xs font-mono text-primary">&lt;reward-button&gt;</code> to send feedback signals when users convert:
        </p>

        <div className="glass rounded-xl p-5 overflow-x-auto border border-border/50 mb-6">
          <pre className="text-sm font-mono">
            <code className="text-emerald-400">{`<reward-button
  variant="A"
  reward="100"
  component-ids='["1", "2"]'>
  Give Reward
</reward-button>`}</code>
          </pre>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          <div className="glass rounded-lg p-4 border border-border/50">
            <code className="text-primary text-sm">variant</code>
            <p className="text-xs text-muted-foreground mt-1">Which variant to attribute reward to (A, B, etc.)</p>
          </div>
          <div className="glass rounded-lg p-4 border border-border/50">
            <code className="text-primary text-sm">reward</code>
            <p className="text-xs text-muted-foreground mt-1">Point value for this conversion (default: 1)</p>
          </div>
          <div className="glass rounded-lg p-4 border border-border/50">
            <code className="text-primary text-sm">component-ids</code>
            <p className="text-xs text-muted-foreground mt-1">JSON array of component IDs to reward</p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="mb-16 scroll-mt-24">
        <h2 className="text-2xl font-semibold mb-6">How It Works</h2>

        <div className="glass rounded-xl overflow-hidden border border-border/50 mb-8">
          <table className="w-full text-sm">
            <thead className="border-b border-border bg-white/5">
              <tr>
                <th className="text-left p-4 font-semibold">Step</th>
                <th className="text-left p-4 font-semibold">Description</th>
              </tr>
            </thead>
            <tbody>
              {[
                { attr: "1. Wrap content", desc: "Place your HTML inside an <ai-opt> element" },
                { attr: "2. AI analyzes", desc: "The multi-agent system analyzes context and user behavior" },
                { attr: "3. Content optimized", desc: "AI generates personalized content variants" },
                { attr: "4. Learn & improve", desc: "System learns from conversions and rewards" },
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

        <h3 className="text-lg font-medium mb-4 mt-8">Variants Data Structure</h3>
        <p className="text-muted-foreground mb-4 text-sm">
          Each user has variant data stored with scoring history for optimization:
        </p>

        <div className="glass rounded-xl p-5 overflow-x-auto border border-border/50">
          <pre className="text-sm font-mono">
            <code className="text-emerald-400">{`{
  "user_id": "12345",

  "variants": {
    "A": {
      "current_html": "<div>...</div>",
      "current_score": 4.3,

      "history": [
        {
          "html": "<div>old version...</div>",
          "score": 3.2,
          "timestamp": "2026-01-17T20:00:00Z"
        },
        {
          "html": "<div>another version...</div>",
          "score": 4.1,
          "timestamp": "2026-01-17T21:00:00Z"
        }
      ]
    },

    "B": {
      "current_html": "<div>...</div>",
      "current_score": 3.0,

      "history": [
        {
          "html": "<div>previous B...</div>",
          "score": 2.7,
          "timestamp": "2026-01-17T19:30:00Z"
        }
      ]
    }
  }
}`}</code>
          </pre>
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
