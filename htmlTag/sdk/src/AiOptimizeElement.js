class AiOptimizeElement extends HTMLElement {
    constructor() {
        super();
        this.originalHTML = "";     // raw content inside the tag
        this.componentId = "";      // <ai-optimize experiment="hero">
    }

    connectedCallback() {
        this.componentId = this.getAttribute("experiment");
        this.originalHTML = this.innerHTML.trim();

        console.log("[AI-OPT] Mounted component:", this.componentId);
        console.log("[AI-OPT] Original content:", this.originalHTML);

        this.requestVariant();
    }

    async requestVariant() {
        try {
            const res = await fetch(`http://localhost:3000/variant`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    experiment: this.componentId,
                    html: this.originalHTML
                })
            });

            const data = await res.json();

            console.log("[AI-OPT] Received variant:", data);

            this.applyVariant(data);

        } catch (err) {
            console.error("[AI-OPT] Variant request failed — using fallback.", err);
        }
    }

    applyVariant(data) {
        if (!data || !data.html) {
            console.log("[AI-OPT] No variant returned. Keeping original.");
            return;
        }

        this.innerHTML = data.html;

        console.log("[AI-OPT] Updated DOM for", this.componentId);
    }
}

customElements.define("ai-optimize", AiOptimizeElement);