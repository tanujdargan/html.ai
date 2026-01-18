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
          Clone the repository and start the backend services:
        </p>
        <div className="glass rounded-xl p-5 overflow-x-auto border border-border/50 mb-4">
          <pre className="text-sm font-mono">
            <code className="text-emerald-400">{`# Clone the repository
git clone https://github.com/tanujdargan/html.ai.git
cd html.ai

# Navigate to the htmlTag directory
cd htmlTag

# Create .env file with your API key
echo "GEMINI_API_KEY=your_gemini_key" > .env

# Start backend and MongoDB with Docker Compose
docker-compose up -d`}</code>
          </pre>
        </div>
        <p className="text-muted-foreground text-sm mb-4">
          This starts the following services:
        </p>
        <ul className="text-muted-foreground text-sm list-disc list-inside space-y-1 ml-2">
          <li><strong>MongoDB</strong> - Database on port 27017</li>
          <li><strong>AI Engine</strong> - Core optimization API on port 3000</li>
          <li><strong>Analytics</strong> - Dashboard API on port 3001</li>
          <li><strong>Demo Pages</strong> - Sample implementations on port 8083</li>
          <li><strong>Dashboard</strong> - Admin panel on port 8084</li>
        </ul>
      </section>

      {/* Quick Start */}
      <section id="quick-start" className="mb-16 scroll-mt-24">
        <h2 className="text-2xl font-semibold mb-6">Quick Start</h2>

        <div className="space-y-6">
          <div className="glass rounded-xl p-5 border border-border/50">
            <div className="flex items-center gap-3 mb-3">
              <span className="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-emerald-500 text-primary-foreground text-sm flex items-center justify-center font-bold">1</span>
              <h3 className="font-medium">Import the SDK components</h3>
            </div>
            <p className="ml-10 text-muted-foreground text-sm mb-3">
              Add the custom element scripts to your HTML page. The SDK includes the AI optimization tag and the reward button component.
            </p>
            <div className="ml-10 glass rounded-lg p-4 overflow-x-auto border border-border/30">
              <pre className="text-sm font-mono">
                <code className="text-emerald-400">{`<!-- AI Optimization Tag -->
<script type="module" src="./sdk/src/AiOptimizeElement_v2.js"></script>

<!-- Reward Button Component -->
<script type="module" src="./sdk/src/RewardButton.js"></script>`}</code>
              </pre>
            </div>
          </div>

          <div className="glass rounded-xl p-5 border border-border/50">
            <div className="flex items-center gap-3 mb-3">
              <span className="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-emerald-500 text-primary-foreground text-sm flex items-center justify-center font-bold">2</span>
              <h3 className="font-medium">Wrap content with ai-opt</h3>
            </div>
            <p className="ml-10 text-muted-foreground text-sm mb-3">
              Wrap any content you want to optimize with the <code className="text-primary">&lt;ai-opt&gt;</code> custom element.
              Assign a unique <code className="text-primary">experiment</code> name and <code className="text-primary">component-id</code> for tracking.
            </p>
            <div className="ml-10 glass rounded-lg p-4 overflow-x-auto border border-border/30">
              <pre className="text-sm font-mono">
                <code className="text-emerald-400">{`<ai-opt experiment="hero-block" component-id="1">
  <div class="hero">
    <img src="product.jpg" alt="Product">
    <div class="hero-info">
      <h2>Your Product Title</h2>
      <p>Product description that AI will personalize.</p>
      <button class="btn">Shop Now</button>
    </div>
  </div>
</ai-opt>`}</code>
              </pre>
            </div>
          </div>

          <div className="glass rounded-xl p-5 border border-border/50">
            <div className="flex items-center gap-3 mb-3">
              <span className="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-emerald-500 text-primary-foreground text-sm flex items-center justify-center font-bold">3</span>
              <h3 className="font-medium">Add reward button for feedback</h3>
            </div>
            <p className="ml-10 text-muted-foreground text-sm mb-3">
              Add a <code className="text-primary">&lt;reward-button&gt;</code> to send reward signals to the AI.
              Use <code className="text-primary">component-ids</code> to pass an array of component IDs that should receive the reward.
            </p>
            <div className="ml-10 glass rounded-lg p-4 overflow-x-auto border border-border/30">
              <pre className="text-sm font-mono">
                <code className="text-emerald-400">{`<!-- Single component reward -->
<reward-button
  variant="A"
  reward="100"
  component-ids='["1"]'>
  Give Reward
</reward-button>

<!-- Multiple components reward (v1.12+) -->
<reward-button
  variant="A"
  reward="50"
  component-ids='["1", "2", "3"]'>
  Reward All
</reward-button>`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Configuration */}
      <section id="configuration" className="mb-16 scroll-mt-24">
        <h2 className="text-2xl font-semibold mb-6">Configuration</h2>

        <h3 className="text-lg font-medium mb-4">ai-opt Attributes</h3>
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
                { attr: "experiment", desc: "Unique experiment name for the component (e.g., \"hero-block\")" },
                { attr: "component-id", desc: "Unique ID to link with reward-button for tracking" },
              ].map((row) => (
                <tr key={row.attr} className="border-b border-border/50 hover:bg-white/5">
                  <td className="p-4 font-mono text-primary">{row.attr}</td>
                  <td className="p-4 text-muted-foreground">{row.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h3 className="text-lg font-medium mb-4">reward-button Attributes</h3>
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
                { attr: "variant", desc: "Variant identifier (A, B, etc.) for tracking which variant received the reward" },
                { attr: "reward", desc: "Point value to assign when clicked (default: 1)" },
                { attr: "component-ids", desc: "JSON array of component IDs to reward (v1.12+). Example: '[\"1\", \"2\"]'" },
                { attr: "component-id", desc: "Single component ID to reward (legacy, use component-ids for arrays)" },
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

      {/* Full Example */}
      <section id="full-example" className="scroll-mt-24">
        <h2 className="text-2xl font-semibold mb-6">Full Example</h2>
        <p className="text-muted-foreground mb-6">
          Here is a complete example showing the AI optimization tag and reward button working together:
        </p>
        <div className="glass rounded-xl p-5 overflow-x-auto border border-border/50">
          <pre className="text-sm font-mono">
            <code className="text-emerald-400">{`<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Shop Demo</title>

    <!-- AI Optimization Tag -->
    <script type="module" src="./sdk/src/AiOptimizeElement_v2.js"></script>

    <!-- Reward Button Component -->
    <script type="module" src="./sdk/src/RewardButton.js"></script>
</head>

<body>
    <h1>AI-Optimized Shop Demo</h1>

    <ai-opt experiment="hero-block" component-id="1">
        <div class="hero">
            <img src="product.jpg" alt="Shoes">
            <div class="hero-info">
                <h2>Comfort Runner Shoes</h2>
                <p>Ultra-light running shoes designed for all-day comfort.</p>
                <button class="btn">Shop Now</button>
            </div>
        </div>
    </ai-opt>

    <!-- Reward button with array of component IDs -->
    <reward-button
        variant="A"
        reward="100"
        component-ids='["1"]'>
        Give Reward
    </reward-button>
</body>
</html>`}</code>
          </pre>
        </div>
      </section>
    </DocsLayout>
  );
}
