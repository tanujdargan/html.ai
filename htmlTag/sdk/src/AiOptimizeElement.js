/**
 * Custom HTML element for AI-powered content optimization
 * Gets personalized variants from backend and tracks conversions
 */
class AiOptimizeElement extends HTMLElement {
    constructor() {
        super();
        this.originalHTML = "";
        this.componentId = "";
        this.sessionId = this.getOrCreateSession();
        this.currentVariantId = null;
        this.apiBaseUrl = "http://localhost:3000";
    }

    connectedCallback() {
        this.componentId = this.getAttribute("experiment");
        this.originalHTML = this.innerHTML.trim();

        console.log("[AI-Optimize] Mounted:", this.componentId);

        // Initialize: get AI-optimized variant
        this.initializeOptimization();

        // Track interactions for reward signal
        this.setupRewardTracking();
    }

    // Get or create session ID
    getOrCreateSession() {
        let sessionId = localStorage.getItem('ai_optimize_session');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('ai_optimize_session', sessionId);
        }
        return sessionId;
    }

    // Initialize and get optimized variant
    async initializeOptimization() {
        try {
            // Track that this component was viewed
            await this.trackEvent('component_viewed', {
                component_type: 'ai-optimize',
                experiment: this.componentId
            });

            // Get AI-optimized variant from multi-agent system
            await this.getOptimizedVariant();

        } catch (err) {
            console.error("[AI-Optimize] Initialization error:", err);
            // Keep original HTML on error
        }
    }

    // Get optimized variant from backend
    async getOptimizedVariant() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/variants/get`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    component_id: this.componentId,
                    original_html: this.originalHTML
                })
            });

            if (!response.ok) {
                throw new Error(`Backend returned ${response.status}`);
            }

            const data = await response.json();

            console.log("[AI-Optimize] Variant received:", data.variant_id);
            console.log("[AI-Optimize] Identity:", data.identity_state);
            console.log("[AI-Optimize] Agent logs:", data.audit_log);

            // Store current variant for reward tracking
            this.currentVariantId = data.variant_id;

            // Apply the optimized content
            this.applyVariant(data.content);

            // Track variant shown
            await this.trackEvent('variant_shown', {
                variant_id: data.variant_id,
                identity_state: data.identity_state,
                confidence: data.confidence
            });

        } catch (err) {
            console.error("[AI-Optimize] Failed to get variant:", err);
            // Keep original content on error
        }
    }

    // Apply variant to the DOM
    applyVariant(content) {
        // Update headline if specified
        const headline = this.querySelector('h1, h2, h3');
        if (headline && content.headline) {
            headline.textContent = content.headline;
            headline.style.transition = 'opacity 0.3s ease';
            headline.style.opacity = '0';
            setTimeout(() => { headline.style.opacity = '1'; }, 50);
        }

        // Update subheadline/description
        const para = this.querySelector('p');
        if (para && content.subheadline) {
            para.textContent = content.subheadline;
            para.style.transition = 'opacity 0.3s ease';
            para.style.opacity = '0';
            setTimeout(() => { para.style.opacity = '1'; }, 100);
        }

        // Update CTA button
        const button = this.querySelector('button');
        if (button && content.cta_text) {
            button.textContent = content.cta_text;
            button.style.transition = 'all 0.3s ease';
            button.style.transform = 'scale(0.95)';
            setTimeout(() => { button.style.transform = 'scale(1)'; }, 150);
        }

        // Apply urgency styling if specified
        if (content.urgency === 'high') {
            const box = this.querySelector('.box, div');
            if (box) {
                box.style.borderLeft = '4px solid #f5576c';
                box.style.background = 'linear-gradient(135deg, #fff5f7 0%, #ffe0e6 100%)';
            }
        }
    }

    // Setup reward tracking for clicks and engagement
    setupRewardTracking() {
        // Track clicks on buttons (primary conversion signal)
        const buttons = this.querySelectorAll('button');
        buttons.forEach(button => {
            button.addEventListener('click', async (e) => {
                console.log("[AI-Optimize] CONVERSION tracked for variant:", this.currentVariantId);

                // Send reward signal to backend
                await this.sendReward('conversion', {
                    variant_id: this.currentVariantId,
                    component_id: this.componentId,
                    conversion_type: 'button_click',
                    button_text: button.textContent
                });
            });
        });

        // Track engagement (time on component)
        const startTime = Date.now();
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(async entry => {
                if (!entry.isIntersecting && !this.hasTrackedEngagement) {
                    const timeSeconds = (Date.now() - startTime) / 1000;

                    // Reward for deep engagement (>5 seconds)
                    if (timeSeconds > 5) {
                        console.log("[AI-Optimize] ENGAGEMENT reward:", timeSeconds.toFixed(1), "seconds");
                        await this.sendReward('engagement', {
                            variant_id: this.currentVariantId,
                            time_seconds: timeSeconds
                        });
                    }

                    this.hasTrackedEngagement = true;
                }
            });
        }, { threshold: 0.5 });

        observer.observe(this);
    }

    // Send reward signal to backend
    async sendReward(rewardType, properties = {}) {
        try {
            await fetch(`${this.apiBaseUrl}/api/rewards/track`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    component_id: this.componentId,
                    reward_type: rewardType,
                    properties: properties
                })
            });

            console.log(`[AI-Optimize] Reward sent: ${rewardType}`);

        } catch (err) {
            console.error("[AI-Optimize] Failed to send reward:", err);
        }
    }

    // Track events
    async trackEvent(eventName, properties = {}) {
        try {
            await fetch(`${this.apiBaseUrl}/api/events/track`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    event_name: eventName,
                    session_id: this.sessionId,
                    component_id: this.componentId,
                    properties: properties
                })
            });
        } catch (err) {
            // Silent fail - don't break user experience
            console.error("[AI-Optimize] Event tracking failed:", err);
        }
    }
}

customElements.define("ai-optimize", AiOptimizeElement);