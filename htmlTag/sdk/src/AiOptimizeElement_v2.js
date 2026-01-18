// AiOptimizeElement_v2.js
export class AiOpt extends HTMLElement {
    constructor() {
        super();
        this.originalHtml = this.innerHTML;
        this.optimized = false;
        this.componentId = this.getAttribute("component-id") || "default";
    }

    connectedCallback() {
        setTimeout(() => this.optimize(), 50);
    }

    async optimize() {
        if (this.optimized) return;

        const ids = window.HtmlAI?.getUser?.() || { user_id: "guest" };
        const contextHtml = document.documentElement.outerHTML;

        const payload = {
            user_id: ids.user_id,
            component_id: this.componentId,
            changingHtml: this.originalHtml,
            contextHtml
        };

        console.log("📤 Sending payload:", payload);

        try {
            const response = await fetch("http://localhost:3000/tagAi", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            console.log("📥 Backend replied:", data);

            if (!response.ok) {
                console.warn("❌ Optimization failed:", data);
                return;
            }

            // ✅ Replace HTML
            this.innerHTML = data.changingHtml;
            this.optimized = true;

            // ✅ Set reward button variant dynamically
            const rewardBtn = document.getElementById("reward-btn");
            if (rewardBtn && data.variant) {
                rewardBtn.setAttribute("variant", data.variant);
            }

        } catch (err) {
            console.error("🔥 ERROR:", err);
        }
    }
}

customElements.define("ai-opt", AiOpt);