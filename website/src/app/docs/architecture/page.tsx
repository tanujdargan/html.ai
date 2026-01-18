"use client";

import DocsLayout from "@/components/DocsLayout";
import { Database, Server, Globe, Box, BarChart3, Store, Megaphone } from "lucide-react";

export default function ArchitecturePage() {
  return (
    <DocsLayout
      title="Architecture"
      description="Overview of the html.ai platform architecture and services."
    >
      {/* System Overview */}
      <section id="overview" className="mb-16 scroll-mt-24">
        <h2 className="text-2xl font-semibold mb-6">System Overview</h2>
        <p className="text-muted-foreground mb-6 leading-relaxed">
          html.ai is a multi-tenant B2B platform providing AI-powered UI personalization with 
          cross-site identity tracking and data sharing between partner businesses.
        </p>

        <div className="grid md:grid-cols-2 gap-4">
          {[
            { title: "Multi-Tenant Architecture", desc: "Complete data isolation with API key auth" },
            { title: "Cross-Site Tracking", desc: "Global UIDs for unified user profiles" },
            { title: "Real-Time Analysis", desc: "AI-powered behavioral identity detection" },
            { title: "Data Sharing", desc: "Privacy-conscious partner data exchange" },
          ].map((item) => (
            <div key={item.title} className="glass rounded-lg p-4 border border-border/50">
              <strong className="text-sm">{item.title}</strong>
              <p className="text-xs text-muted-foreground mt-1">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Services */}
      <section id="services" className="mb-16 scroll-mt-24">
        <h2 className="text-2xl font-semibold mb-6">Services</h2>
        <p className="text-muted-foreground mb-8 leading-relaxed">
          The platform consists of 7 containerized services:
        </p>

        <div className="space-y-4">
          {[
            { icon: Database, name: "MongoDB", port: "27017", desc: "Primary database with persistent storage", color: "emerald" },
            { icon: Server, name: "AI Backend", port: "3000", desc: "FastAPI app with multi-agent AI system", color: "blue" },
            { icon: Globe, name: "Tracking Service", port: "3001", desc: "Cross-site identity sync domain", color: "purple" },
            { icon: Box, name: "SDK Server", port: "8080", desc: "Nginx serving JavaScript SDK files", color: "amber" },
            { icon: BarChart3, name: "Dashboard", port: "8081", desc: "Admin UI for analytics and config", color: "cyan" },
            { icon: Store, name: "Demo Store", port: "8082", desc: "Example e-commerce integration", color: "pink" },
            { icon: Megaphone, name: "Marketing", port: "4000", desc: "Next.js landing page and docs", color: "rose" },
          ].map((service) => {
            const Icon = service.icon;
            return (
              <div key={service.name} className="glass rounded-xl p-5 border border-border/50 flex items-center gap-4">
                <div className={`w-10 h-10 rounded-lg bg-${service.color}-500/20 flex items-center justify-center flex-shrink-0`}>
                  <Icon className={`text-${service.color}-400`} size={20} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="font-medium">{service.name}</h3>
                    <code className="text-xs text-muted-foreground font-mono">:{service.port}</code>
                  </div>
                  <p className="text-sm text-muted-foreground">{service.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Docker Setup */}
      <section id="docker" className="mb-16 scroll-mt-24">
        <h2 className="text-2xl font-semibold mb-6">Docker Setup</h2>
        
        <div className="glass rounded-xl p-5 overflow-x-auto border border-border/50 mb-6">
          <pre className="text-sm font-mono">
            <code className="text-emerald-400">{`# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# With Gemini API key (for AI features)
GEMINI_API_KEY=your_key docker-compose up -d`}</code>
          </pre>
        </div>

        <div className="glass rounded-xl p-5 border border-border/50">
          <h3 className="font-medium mb-3">Port Reference</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
            {[
              { port: "27017", name: "MongoDB" },
              { port: "3000", name: "API" },
              { port: "3001", name: "Tracking" },
              { port: "8080", name: "SDK" },
              { port: "8081", name: "Dashboard" },
              { port: "8082", name: "Demo" },
              { port: "4000", name: "Marketing" },
            ].map((item) => (
              <div key={item.port} className="flex items-center gap-2 bg-black/20 rounded-lg p-2">
                <code className="font-mono text-primary text-xs">{item.port}</code>
                <span className="text-muted-foreground text-xs">{item.name}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Database */}
      <section id="database" className="scroll-mt-24">
        <h2 className="text-2xl font-semibold mb-6">Database</h2>
        <p className="text-muted-foreground mb-6 leading-relaxed">
          MongoDB collections for multi-tenant data storage:
        </p>

        <div className="grid md:grid-cols-2 gap-4">
          {[
            { name: "businesses", desc: "Registered accounts with API credentials" },
            { name: "events", desc: "Behavioral events from user interactions" },
            { name: "users", desc: "User sessions per business" },
            { name: "variants", desc: "Content variants shown with conversion tracking" },
            { name: "global_users", desc: "Cross-site identity mappings" },
            { name: "data_sharing_agreements", desc: "Partner sharing configurations" },
          ].map((collection) => (
            <div key={collection.name} className="glass rounded-lg p-4 border border-border/50">
              <code className="font-mono text-primary text-sm">{collection.name}</code>
              <p className="text-xs text-muted-foreground mt-1">{collection.desc}</p>
            </div>
          ))}
        </div>

        <p className="text-sm text-muted-foreground mt-6">
          See <code className="bg-black/30 px-1.5 py-0.5 rounded text-xs">scripts/mongo-init.js</code> for 
          indexes and demo data setup.
        </p>
      </section>
    </DocsLayout>
  );
}
