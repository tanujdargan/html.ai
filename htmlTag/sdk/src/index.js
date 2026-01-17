const API_URL = "http://localhost:8000";
const POLL_INTERVAL = 5000; // Check every 5 seconds

class AiOptimizeElement extends HTMLElement {
    constructor() {
        super();
        this.originalHTML = "";
        this.currentHTML = "";
        this.experimentId = "";
        this.pollTimer = null;
    }

    connectedCallback() {
        this.experimentId = this.getAttribute("experiment") || "default";
        this.originalHTML = this.innerHTML.trim();
        this.currentHTML = this.originalHTML;

        console.log(`[ai-optimize] Mounted: ${this.experimentId}`);

        // Initial check
        this.checkForUpdate();

        // Start polling
        this.pollTimer = setInterval(() => this.checkForUpdate(), POLL_INTERVAL);
    }

    disconnectedCallback() {
        // Stop polling when element is removed
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
    }

    async checkForUpdate() {
        try {
            const res = await fetch(`${API_URL}/optimize`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    experiment: this.experimentId,
                    html: this.originalHTML
                })
            });

            if (!res.ok) {
                console.error(`[ai-optimize] Server error: ${res.status}`);
                return;
            }

            const data = await res.json();

            if (data.updated && data.html !== this.currentHTML) {
                console.log(`[ai-optimize] Update received for: ${this.experimentId}`);
                this.currentHTML = data.html;
                this.innerHTML = data.html;
            }

        } catch (err) {
            console.error(`[ai-optimize] Error checking for update:`, err.message);
        }
    }

    // Allow manual refresh
    refresh() {
        this.checkForUpdate();
    }

    // Reset to original content
    reset() {
        this.currentHTML = this.originalHTML;
        this.innerHTML = this.originalHTML;
        console.log(`[ai-optimize] Reset to original: ${this.experimentId}`);
    }
}

customElements.define("ai-optimize", AiOptimizeElement);

console.log("[ai-optimize] SDK loaded");
