"use client";

import DocsLayout from "@/components/DocsLayout";

export default function ApiReferencePage() {
  return (
    <DocsLayout
      title="API Reference"
      description="SDK methods and auto-tracked events."
    >
      {/* SDK Methods */}
      <section id="sdk-methods" className="mb-16 scroll-mt-24">
        <h2 className="text-2xl font-semibold mb-6">SDK Methods</h2>

        <div className="space-y-4">
          {[
            { 
              method: "HtmlAI.init(options)", 
              desc: "Initialize with custom config (apiKey, apiBaseUrl, trackingDomain, debug)" 
            },
            { 
              method: "HtmlAI.track(eventName, componentId?, properties?)", 
              desc: "Track custom events with optional component context and properties" 
            },
            { 
              method: "HtmlAI.getUser()", 
              desc: "Returns { user_id, session_id, global_uid }" 
            },
            { 
              method: "HtmlAI.onSync(callback)", 
              desc: "Callback when cross-site identity sync completes" 
            },
            { 
              method: "HtmlAI.flush()", 
              desc: "Force send all queued events immediately" 
            },
          ].map((item) => (
            <div key={item.method} className="glass rounded-xl p-5 border border-border/50">
              <code className="font-mono text-primary">{item.method}</code>
              <p className="text-muted-foreground text-sm mt-2">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Auto-tracked Events */}
      <section id="auto-tracked" className="scroll-mt-24">
        <h2 className="text-2xl font-semibold mb-6">Auto-tracked Events</h2>
        <p className="text-muted-foreground mb-6">
          The SDK automatically tracks these behavioral signals:
        </p>

        <div className="grid md:grid-cols-2 gap-3">
          {[
            { event: "page_viewed", desc: "Page load with URL and referrer" },
            { event: "scroll_depth_reached", desc: "Scroll depth percentage" },
            { event: "scroll_fast", desc: "Rapid scrolling (>500px)" },
            { event: "scroll_direction_change", desc: "Direction changes" },
            { event: "rage_click", desc: "3+ clicks in 500ms" },
            { event: "dead_click", desc: "Click on non-interactive element" },
            { event: "mouse_hesitation", desc: "Mouse idle for 2+ seconds" },
            { event: "hover", desc: "Hover on data-track-hover elements" },
            { event: "tab_hidden / tab_visible", desc: "Tab visibility changes" },
            { event: "component_viewed", desc: "ai-optimize component in view" },
          ].map((item) => (
            <div key={item.event} className="glass rounded-lg p-3 border border-border/50 flex items-start gap-3">
              <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0"></span>
              <div>
                <code className="font-mono text-primary text-sm">{item.event}</code>
                <p className="text-muted-foreground text-xs mt-0.5">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>

        <p className="text-sm text-muted-foreground mt-8">
          For REST API documentation, see the FastAPI docs at <code className="bg-black/30 px-1.5 py-0.5 rounded text-xs">/docs</code> on the API server.
        </p>
      </section>

      {/* Variants Data Structure */}
      <section id="variants" className="mt-16 scroll-mt-24">
        <h2 className="text-2xl font-semibold mb-6">Variants Data Structure</h2>
        <p className="text-muted-foreground mb-6">
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
    </DocsLayout>
  );
}
