/**
 * <ai-optimize> Custom Element - v2.0
 * 
 * Developer-friendly wrapper for AI-powered content optimization
 * 
 * Usage:
 *   <ai-optimize experiment="hero-cta">
 *     <h1>Your headline</h1>
 *     <p>Your content</p>
 *     <button>Click me</button>
 *   </ai-optimize>
 * 
 * Backend: 4-agent system (Analytics → Identity → Decision → Guardrail)
 * 
 * Sponsor alignment:
 * - Foresters: Multi-agent orchestration with audit logs
 * - Amplitude: Behavioral vectors (NOT user categorization!) + self-improving loop
 * - Shopify: E-commerce conversion optimization
 */
class AiOptimizeElement extends HTMLElement {
    constructor() {
        super();
        this.originalHTML = "";
        this.componentId = "";
        this.userId = this.getOrCreateUserId();  // Persistent cookie-based ID
        this.sessionId = this.getOrCreateSession();
        this.currentVariantId = null;
        this.apiBaseUrl = "http://localhost:3000";  // Updated to port 3000
        this.startTime = Date.now();
    }

    connectedCallback() {
        this.componentId = this.getAttribute("experiment") || "unnamed";
        this.originalHTML = this.innerHTML.trim();

        console.log(`[ai-optimize] Mounted: ${this.componentId}`);
        console.log(`[ai-optimize] User ID: ${this.userId}`);

        // Initialize: get AI-optimized variant from multi-agent system
        this.initializeOptimization();

        // Setup event tracking for behavioral vector
        this.setupBehavioralTracking();

        // Setup reward tracking for self-improving loop
        this.setupRewardTracking();
    }

    // ========================================
    // User & Session Management
    // ========================================
    
    getOrCreateUserId() {
        let userId = this.getCookie('ai_optimize_user_id');
        if (!userId) {
            userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            this.setCookie('ai_optimize_user_id', userId, 365); // 1 year cookie
        }
        return userId;
    }

    getOrCreateSession() {
        let sessionId = sessionStorage.getItem('ai_optimize_session');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            sessionStorage.setItem('ai_optimize_session', sessionId);
        }
        return sessionId;
    }

    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    setCookie(name, value, days) {
        const expires = new Date(Date.now() + days * 864e5).toUTCString();
        document.cookie = `${name}=${value}; expires=${expires}; path=/`;
    }

    // ========================================
    // Multi-Agent Optimization (THE MAGIC)
    // ========================================

    async initializeOptimization() {
        try {
            console.log(`[ai-optimize] Requesting optimized variant from multi-agent system...`);
            
            const response = await fetch(`${this.apiBaseUrl}/api/optimize`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    component_id: this.componentId,
                    html: this.originalHTML,
                    context_html: document.body.innerHTML.substring(0, 1000) // First 1KB of page
                })
            });

            if (!response.ok) {
                throw new Error(`Backend returned ${response.status}`);
            }

            const data = await response.json();

            // Log multi-agent results
            console.log(`[ai-optimize] ✓ Variant: ${data.variant_id}`);
            console.log(`[ai-optimize] ✓ Identity: ${data.identity_state} (confidence: ${data.confidence?.toFixed(2)})`);
            
            if (data.audit_log && data.audit_log.length > 0) {
                console.log(`[ai-optimize] ✓ Agent Communication Log:`);
                data.audit_log.forEach(entry => console.log(`  - ${entry}`));
            }

            if (data.behavioral_vector) {
                console.log(`[ai-optimize] ✓ Behavioral Vector:`, data.behavioral_vector);
            }

            // Store variant ID for reward tracking
            this.currentVariantId = data.variant_id;

            // Apply the optimized content
            this.applyVariant(data.content);

        } catch (err) {
            console.error(`[ai-optimize] Error:`, err);
            // Keep original content on error
        }
    }

    applyVariant(content) {
        /**
         * Apply AI-generated variant to DOM
         * Supports different content types from Decision Agent
         */
        
        // Update headline
        const headline = this.querySelector('h1, h2, h3');
        if (headline && content.headline) {
            this.animateUpdate(headline, content.headline);
        }

        // Update subheadline/description
        const para = this.querySelector('p');
        if (para && content.subheadline) {
            this.animateUpdate(para, content.subheadline, 100);
        }

        // Update CTA button
        const button = this.querySelector('button, a.button');
        if (button && content.cta_text) {
            this.animateUpdate(button, content.cta_text, 150);
        }

        // Apply urgency styling
        if (content.urgency === 'high' || content.urgency === 'extreme') {
            this.applyUrgencyStyle(content.urgency);
        }

        // Add trust badges if present
        if (content.trust_badges && Array.isArray(content.trust_badges)) {
            this.addTrustBadges(content.trust_badges);
        }

        // Add countdown timer if present
        if (content.countdown) {
            this.addCountdown(content.countdown);
        }
    }

    animateUpdate(element, newText, delay = 0) {
        element.style.transition = 'opacity 0.3s ease';
        element.style.opacity = '0';
        setTimeout(() => {
            element.textContent = newText;
            element.style.opacity = '1';
        }, delay);
    }

    applyUrgencyStyle(urgency) {
        const container = this.querySelector('.box, div');
        if (!container) return;

        if (urgency === 'extreme') {
            container.style.borderLeft = '5px solid #f5576c';
            container.style.background = 'linear-gradient(135deg, #fff0f2 0%, #ffe0e6 100%)';
            container.style.boxShadow = '0 4px 12px rgba(245, 87, 108, 0.2)';
        } else if (urgency === 'high') {
            container.style.borderLeft = '4px solid #f5576c';
            container.style.background = 'linear-gradient(135deg, #fff5f7 0%, #ffe8ec 100%)';
        }
    }

    addTrustBadges(badges) {
        const badgeContainer = document.createElement('div');
        badgeContainer.style.cssText = 'display: flex; gap: 12px; margin-top: 16px; flex-wrap: wrap;';
        
        badges.forEach(badge => {
            const badgeEl = document.createElement('span');
            badgeEl.textContent = `✓ ${badge}`;
            badgeEl.style.cssText = 'font-size: 12px; color: #28a745; font-weight: 500;';
            badgeContainer.appendChild(badgeEl);
        });
        
        this.appendChild(badgeContainer);
    }

    addCountdown(time) {
        const countdownEl = document.createElement('div');
        countdownEl.style.cssText = 'font-size: 20px; font-weight: bold; color: #f5576c; margin-top: 12px;';
        countdownEl.textContent = `⏰ ${time}`;
        this.appendChild(countdownEl);
        // TODO: Make this a real countdown timer
    }

    // ========================================
    // Behavioral Event Tracking (Amplitude-style)
    // ========================================

    setupBehavioralTracking() {
        /**
         * Track behavioral events to build behavioral vector
         * NOT user categorization - just behavior patterns!
         * 
         * Events tracked:
         * - scroll_depth
         * - time_on_component
         * - hover (engagement signal)
         * - click
         */

        // Track scroll depth
        let maxScrollDepth = 0;
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const depth = Math.round(entry.intersectionRatio * 100);
                    if (depth > maxScrollDepth) {
                        maxScrollDepth = depth;
                        this.trackEvent('scroll_depth_reached', {
                            depth_percent: depth,
                            component_id: this.componentId
                        });
                    }
                }
            });
        }, { threshold: [0.25, 0.5, 0.75, 1.0] });
        
        observer.observe(this);

        // Track hover (engagement signal)
        this.addEventListener('mouseenter', () => {
            this.trackEvent('component_hover', {
                component_id: this.componentId,
                variant_id: this.currentVariantId
            });
        });

        // Track time on component
        this.trackTimeOnComponent();
    }

    trackTimeOnComponent() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (!entry.isIntersecting && !this.hasTrackedTime) {
                    const timeSeconds = (Date.now() - this.startTime) / 1000;
                    
                    this.trackEvent('time_on_component', {
                        component_id: this.componentId,
                        variant_id: this.currentVariantId,
                        time_seconds: timeSeconds
                    });
                    
                    this.hasTrackedTime = true;
                }
            });
        }, { threshold: 0.5 });
        
        observer.observe(this);
    }

    async trackEvent(eventName, properties = {}) {
        try {
            await fetch(`${this.apiBaseUrl}/api/events/track`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    session_id: this.sessionId,
                    event_name: eventName,
                    component_id: this.componentId,
                    properties: properties
                })
            });
        } catch (err) {
            // Silent fail - don't break UX
            console.debug('[ai-optimize] Event tracking failed:', err);
        }
    }

    // ========================================
    // Reward Tracking (Self-Improving Loop)
    // ========================================

    setupRewardTracking() {
        /**
         * Track reward signals for the self-improving loop
         * This creates the feedback: behavioral vector → variant → conversion
         * 
         * The system learns which variants work best for each identity state
         */

        // Track button clicks (primary conversion signal)
        const buttons = this.querySelectorAll('button, a.button');
        buttons.forEach(button => {
            button.addEventListener('click', async () => {
                console.log(`[ai-optimize] 🎯 CONVERSION: Button clicked for variant ${this.currentVariantId}`);
                
                await this.sendReward('click', {
                    button_text: button.textContent,
                    component_id: this.componentId
                });
            });
        });

        // Track deep engagement (>5 seconds)
        setTimeout(() => {
            this.sendReward('engagement', {
                time_seconds: 5,
                component_id: this.componentId
            });
        }, 5000);
    }

    async sendReward(rewardType, properties = {}) {
        if (!this.currentVariantId) return;

        try {
            await fetch(`${this.apiBaseUrl}/api/reward`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    component_id: this.componentId,
                    variant_id: this.currentVariantId,
                    reward_type: rewardType,
                    properties: properties
                })
            });

            console.log(`[ai-optimize] Reward sent: ${rewardType}`);

        } catch (err) {
            console.error('[ai-optimize] Failed to send reward:', err);
        }
    }
}

// Register the custom element
customElements.define("ai-optimize", AiOptimizeElement);

console.log('[ai-optimize] SDK loaded - wrap any HTML in <ai-optimize experiment="name">');
