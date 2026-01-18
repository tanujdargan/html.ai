class RewardButton extends HTMLElement {
    constructor() {
        super();
        this.variant = this.getAttribute("variant") || null;   // A or B
        this.reward = Number(this.getAttribute("reward") || 1); // +1 default
        const rawIds = this.getAttribute("component-ids") || this.getAttribute("component-id") || "default";
        let componentIds = [];
        try {
            const parsed = JSON.parse(rawIds);
            componentIds = Array.isArray(parsed) ? parsed : [parsed];
        } catch {
            componentIds = [rawIds];
        }
        this.componentIds = componentIds;
    }

    connectedCallback() {
        this.style.cursor = "pointer";

        this.addEventListener("click", () => this.sendReward());
    }

    async sendReward() {
        const ids = window.HtmlAI?.getUser?.() || { user_id: "guest" };
        const contextHtml = document.documentElement.outerHTML;

        const payload = {
            user_id: ids.user_id,
            variantAttributed: this.variant,
            reward: this.reward,
            contextHtml: contextHtml,
            component_ids: this.componentIds
        };

        console.log("🎯 Sending REWARD payload → /rewardTag:", payload);

        try {
            const response = await fetch("http://localhost:3000/rewardTag", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            console.log("🏆 rewardTag response:", data);

        } catch (err) {
            console.error("🔥 REWARD BUTTON ERROR:", err);
        }
    }
}

customElements.define("reward-button", RewardButton);