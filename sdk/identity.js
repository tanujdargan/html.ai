class AiOptimizeElement extends HTMLElement {
    constructor() {
        super();
        this.originalHTML = "";     // raw content inside the tag
        this.componentId = "";      // the experiment name
    }

    connectedCallback() {
        this.componentId = this.getAttribute("experiment") || "default";
        this.originalHTML = this.innerHTML.trim();

        console.log("[AI-OPT] Mounted component:", this.componentId);
        console.log("[AI-OPT] Original content:", this.originalHTML);

        this.requestVariant();
    }

    async requestVariant() {
        try {
            const response = await fetch("http://localhost:3000/variant", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    experiment: this.componentId,
                    html: this.originalHTML
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            console.log("[AI-OPT] Received variant:", data);

            this.applyVariant(data);

        } catch (err) {
            console.error("[AI-OPT] Variant request failed — reverting to original.", err);
        }
    }

    applyVariant(data) {
        // If backend does not send HTML, use original
        if (!data || !data.html) {
            console.log("[AI-OPT] No variant returned. Keeping original.");
            return;
        }

        // Replace component content with personalized variant
        this.innerHTML = data.html;

        console.log(`[AI-OPT] Updated DOM for experiment "${this.componentId}"`);
    }
}

// Register the custom tag globally
customElements.define("ai-optimize", AiOptimizeElement);