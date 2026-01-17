class AiOptimizeElement extends HTMLElement {
    constructor() {
        super();
        this.originalHTML = "";
        this.componentId = "";
    }

    connectedCallback() {
        this.componentId = this.getAttribute("experiment");
        this.originalHTML = this.innerHTML.trim();

        console.log("[AI-OPT] Mounted:", this.componentId);
        console.log("[AI-OPT] Sending HTML to backend…");

        this.sendToBackend();
    }

    async sendToBackend() {
        try {
            const res = await fetch("http://localhost:3000/log-html", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    experiment: this.componentId,
                    html: this.originalHTML
                })
            });

            const data = await res.json();
            console.log("[AI-OPT] Backend responded:", data);

        } catch (err) {
            console.error("[AI-OPT] Error sending HTML:", err);
        }
    }
}

customElements.define("ai-optimize", AiOptimizeElement);