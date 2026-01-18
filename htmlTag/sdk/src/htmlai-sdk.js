/**
 * html.ai SDK - Multi-Tenant B2B Edition
 *
 * Features:
 * - API key authentication
 * - Cross-site user tracking via central sync
 * - Behavioral event collection
 * - AI-powered component optimization
 *
 * Usage:
 * <script src="https://cdn.htmlai.com/sdk.js"
 *         data-api-key="pk_live_xxxxx"
 *         data-tracking-domain="https://tracking.htmlai.com">
 * </script>
 */

(function(window, document) {
    'use strict';

    // ========================================
    // Configuration
    // ========================================
    const CONFIG = {
        apiKey: null,
        businessId: null,  // Will be derived from API key or fetched
        apiBaseUrl: 'http://localhost:3000',
        trackingDomain: 'http://localhost:3000',  // Central sync domain
        userIdCookie: 'htmlai_uid',
        globalIdCookie: 'htmlai_guid',
        sessionKey: 'htmlai_session',
        cookieMaxAgeDays: 365,
        batchSize: 10,
        batchInterval: 5000,  // 5 seconds
        debug: false
    };

    // ========================================
    // Cookie Utilities
    // ========================================
    const CookieUtils = {
        set(name, value, days = CONFIG.cookieMaxAgeDays) {
            const expires = new Date(Date.now() + days * 864e5).toUTCString();
            document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
        },

        get(name) {
            const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
            return match ? decodeURIComponent(match[2]) : null;
        },

        delete(name) {
            document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
        }
    };

    // ========================================
    // UUID Generator
    // ========================================
    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    // ========================================
    // User Identity Manager
    // ========================================
    const UserManager = {
        userId: null,
        globalId: null,
        sessionId: null,

        init() {
            // Get or create local user ID
            this.userId = CookieUtils.get(CONFIG.userIdCookie);
            if (!this.userId) {
                this.userId = 'user_' + generateUUID();
                CookieUtils.set(CONFIG.userIdCookie, this.userId);
                log('New user ID created:', this.userId);
            }

            // Get or create session ID
            this.sessionId = sessionStorage.getItem(CONFIG.sessionKey);
            if (!this.sessionId) {
                this.sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                sessionStorage.setItem(CONFIG.sessionKey, this.sessionId);
                log('New session created:', this.sessionId);
            }

            // Check for existing global ID
            this.globalId = CookieUtils.get(CONFIG.globalIdCookie);

            return this;
        },

        setGlobalId(guid) {
            this.globalId = guid;
            CookieUtils.set(CONFIG.globalIdCookie, guid);
            log('Global ID set:', guid);
        },

        getIds() {
            return {
                user_id: this.userId,
                session_id: this.sessionId,
                global_uid: this.globalId
            };
        }
    };

    // ========================================
    // Cross-Site Sync Manager
    // ========================================
    const SyncManager = {
        iframe: null,
        synced: false,
        callbacks: [],

        init() {
            if (!CONFIG.trackingDomain) {
                log('No tracking domain configured, skipping cross-site sync');
                return;
            }

            // Listen for messages from sync iframe
            window.addEventListener('message', (event) => {
                // Verify origin
                if (!event.origin.includes(new URL(CONFIG.trackingDomain).host)) {
                    return;
                }

                if (event.data && event.data.type === 'htmlai_sync') {
                    this.handleSyncResponse(event.data);
                }
            });

            // Create hidden sync iframe
            this.createSyncIframe();
        },

        createSyncIframe() {
            this.iframe = document.createElement('iframe');
            this.iframe.src = `${CONFIG.trackingDomain}/sync/iframe`;
            this.iframe.style.cssText = 'display:none;width:0;height:0;border:0;';
            this.iframe.setAttribute('aria-hidden', 'true');

            document.body.appendChild(this.iframe);
            log('Sync iframe created');
        },

        handleSyncResponse(data) {
            if (data.global_uid) {
                UserManager.setGlobalId(data.global_uid);
                this.synced = true;

                // Link local UID to global UID on server
                this.linkIdentity(data.global_uid);

                // Execute pending callbacks
                this.callbacks.forEach(cb => cb(data.global_uid));
                this.callbacks = [];

                log('Cross-site sync complete:', data.global_uid);
            }
        },

        async linkIdentity(globalUid) {
            try {
                await fetch(`${CONFIG.apiBaseUrl}/sync/link`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': CONFIG.apiKey,
                        'X-Global-UID': globalUid
                    },
                    body: JSON.stringify({
                        business_id: CONFIG.businessId,
                        local_uid: UserManager.userId
                    })
                });
            } catch (err) {
                console.error('[html.ai] Failed to link identity:', err);
            }
        },

        onSync(callback) {
            if (this.synced && UserManager.globalId) {
                callback(UserManager.globalId);
            } else {
                this.callbacks.push(callback);
            }
        }
    };

    // ========================================
    // Event Tracker
    // ========================================
    const EventTracker = {
        queue: [],
        batchTimer: null,

        init() {
            // Start batch timer
            this.batchTimer = setInterval(() => this.flush(), CONFIG.batchInterval);

            // Flush on page unload
            window.addEventListener('beforeunload', () => this.flush());

            // Auto-track page view
            this.track('page_viewed', null, {
                url: window.location.href,
                referrer: document.referrer,
                title: document.title
            });
        },

        track(eventName, componentId = null, properties = {}) {
            const event = {
                event_name: eventName,
                component_id: componentId,
                properties: {
                    ...properties,
                    timestamp: new Date().toISOString(),
                    url: window.location.href
                }
            };

            this.queue.push(event);
            log('Event queued:', eventName, componentId);

            // Flush if batch size reached
            if (this.queue.length >= CONFIG.batchSize) {
                this.flush();
            }
        },

        async flush() {
            if (this.queue.length === 0) return;

            const events = [...this.queue];
            this.queue = [];

            const ids = UserManager.getIds();

            try {
                const response = await fetch(`${CONFIG.apiBaseUrl}/api/events/batch`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': CONFIG.apiKey
                    },
                    body: JSON.stringify({
                        user_id: ids.user_id,
                        session_id: ids.session_id,
                        global_uid: ids.global_uid,
                        events: events
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                log('Batch sent:', events.length, 'events');
            } catch (err) {
                console.error('[html.ai] Failed to send events:', err);
                // Re-queue failed events
                this.queue = [...events, ...this.queue];
            }
        }
    };

    // ========================================
    // Behavioral Tracking
    // ========================================
    const BehaviorTracker = {
        scrollData: { lastY: 0, direction: null, fastScrolls: 0 },
        clickData: { lastTime: 0, count: 0 },
        hoverData: { element: null, startTime: 0 },

        init() {
            // Scroll tracking
            let scrollTimeout;
            window.addEventListener('scroll', () => {
                const currentY = window.scrollY;
                const direction = currentY > this.scrollData.lastY ? 'down' : 'up';

                // Detect direction change
                if (this.scrollData.direction && direction !== this.scrollData.direction) {
                    EventTracker.track('scroll_direction_change', null, {
                        from: this.scrollData.direction,
                        to: direction,
                        position: currentY
                    });
                }

                // Detect fast scroll
                clearTimeout(scrollTimeout);
                const scrollDelta = Math.abs(currentY - this.scrollData.lastY);
                if (scrollDelta > 500) {
                    this.scrollData.fastScrolls++;
                    EventTracker.track('scroll_fast', null, {
                        delta: scrollDelta,
                        position: currentY
                    });
                }

                this.scrollData.lastY = currentY;
                this.scrollData.direction = direction;

                // Track scroll depth
                scrollTimeout = setTimeout(() => {
                    const depth = Math.round((currentY / (document.body.scrollHeight - window.innerHeight)) * 100);
                    EventTracker.track('scroll_depth_reached', null, { depth_percent: depth });
                }, 150);
            }, { passive: true });

            // Click tracking (rage clicks, dead clicks)
            document.addEventListener('click', (e) => {
                const now = Date.now();

                // Rage click detection (3+ clicks within 500ms)
                if (now - this.clickData.lastTime < 500) {
                    this.clickData.count++;
                    if (this.clickData.count >= 3) {
                        EventTracker.track('rage_click', null, {
                            target: e.target.tagName,
                            x: e.clientX,
                            y: e.clientY
                        });
                        this.clickData.count = 0;
                    }
                } else {
                    this.clickData.count = 1;
                }
                this.clickData.lastTime = now;

                // Dead click detection (click on non-interactive element)
                const interactive = ['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'];
                if (!interactive.includes(e.target.tagName) && !e.target.onclick) {
                    EventTracker.track('dead_click', null, {
                        target: e.target.tagName,
                        x: e.clientX,
                        y: e.clientY
                    });
                }
            });

            // Hover tracking
            document.addEventListener('mouseover', (e) => {
                if (e.target.hasAttribute('data-track-hover')) {
                    this.hoverData.element = e.target;
                    this.hoverData.startTime = Date.now();
                }
            });

            document.addEventListener('mouseout', (e) => {
                if (this.hoverData.element === e.target) {
                    const duration = Date.now() - this.hoverData.startTime;
                    if (duration > 500) {  // Only track meaningful hovers
                        EventTracker.track('hover', e.target.getAttribute('data-component-id'), {
                            duration_ms: duration
                        });
                    }
                    this.hoverData.element = null;
                }
            });

            // Tab visibility
            document.addEventListener('visibilitychange', () => {
                EventTracker.track(document.hidden ? 'tab_hidden' : 'tab_visible');
            });

            // Mouse hesitation (mouse stops for 2+ seconds)
            let hesitationTimeout;
            document.addEventListener('mousemove', () => {
                clearTimeout(hesitationTimeout);
                hesitationTimeout = setTimeout(() => {
                    EventTracker.track('mouse_hesitation');
                }, 2000);
            });
        }
    };

    // ========================================
    // AI Optimize Component
    // ========================================
    class AiOptimizeElement extends HTMLElement {
        constructor() {
            super();
            this.optimized = false;
            this.originalContent = '';
        }

        connectedCallback() {
            this.originalContent = this.innerHTML;
            this.componentId = this.getAttribute('component-id') || 'component_' + Math.random().toString(36).substr(2, 9);

            // Track view
            EventTracker.track('component_viewed', this.componentId);

            // Request optimization
            this.optimize();
        }

        async optimize() {
            if (this.optimized) return;

            const ids = UserManager.getIds();

            try {
                const response = await fetch(`${CONFIG.apiBaseUrl}/api/optimize`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': CONFIG.apiKey
                    },
                    body: JSON.stringify({
                        user_id: ids.user_id,
                        component_id: this.componentId,
                        html: this.originalContent,
                        global_uid: ids.global_uid
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                const result = await response.json();
                this.applyVariant(result);
                this.optimized = true;

                log('Component optimized:', this.componentId, result.variant_id);

            } catch (err) {
                console.error('[html.ai] Optimization failed:', err);
            }
        }

        applyVariant(result) {
            // Find elements to update
            const headline = this.querySelector('[data-ai="headline"]');
            const subheadline = this.querySelector('[data-ai="subheadline"]');
            const cta = this.querySelector('[data-ai="cta"]');

            if (result.content) {
                if (headline && result.content.headline) {
                    headline.textContent = result.content.headline;
                }
                if (subheadline && result.content.subheadline) {
                    subheadline.textContent = result.content.subheadline;
                }
                if (cta && result.content.cta_text) {
                    cta.textContent = result.content.cta_text;
                }
            }

            // Store variant info for reward tracking
            this.variantId = result.variant_id;
            this.setAttribute('data-variant', result.variant_id);
            this.setAttribute('data-identity', result.identity_state);

            // Add click handler for CTA
            if (cta) {
                cta.addEventListener('click', () => this.trackReward());
            }
        }

        async trackReward() {
            const ids = UserManager.getIds();

            try {
                await fetch(`${CONFIG.apiBaseUrl}/api/reward`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': CONFIG.apiKey
                    },
                    body: JSON.stringify({
                        user_id: ids.user_id,
                        component_id: this.componentId,
                        variant_id: this.variantId,
                        reward_type: 'click'
                    })
                });

                log('Reward tracked:', this.componentId, this.variantId);

            } catch (err) {
                console.error('[html.ai] Reward tracking failed:', err);
            }
        }
    }

    // ========================================
    // Logging
    // ========================================
    function log(...args) {
        if (CONFIG.debug) {
            console.log('[html.ai]', ...args);
        }
    }

    // ========================================
    // Public API
    // ========================================
    const HtmlAI = {
        init(options = {}) {
            // Merge options
            Object.assign(CONFIG, options);

            // Get config from script tag
            const script = document.currentScript || document.querySelector('script[data-api-key]') || document.querySelector('script[src*="htmlai-sdk"]');
            if (script) {
                CONFIG.apiKey = script.getAttribute('data-api-key') || CONFIG.apiKey;
                CONFIG.trackingDomain = script.getAttribute('data-tracking-domain') || CONFIG.trackingDomain;
                CONFIG.apiBaseUrl = script.getAttribute('data-api-url') || CONFIG.apiBaseUrl;
                CONFIG.debug = script.hasAttribute('data-debug');
            }

            if (!CONFIG.apiKey) {
                console.warn('[html.ai] API key not found. Set via data-api-key attribute or HtmlAI.init({apiKey: "..."})');
                // Don't return - allow manual initialization later
            }

            // Derive business ID from API key pattern or fetch it
            // API keys follow pattern: pk_demo_shoes_123 -> biz_shoes
            if (CONFIG.apiKey && !CONFIG.businessId) {
                const match = CONFIG.apiKey.match(/pk_demo_(\w+)_/);
                if (match) {
                    CONFIG.businessId = 'biz_' + match[1];
                } else {
                    // Default fallback - will be updated when we fetch from server
                    CONFIG.businessId = 'unknown';
                }
            }

            log('Initializing with config:', CONFIG);

            // Initialize modules
            UserManager.init();
            SyncManager.init();
            EventTracker.init();
            BehaviorTracker.init();

            // Register custom element
            if (!customElements.get('ai-optimize')) {
                customElements.define('ai-optimize', AiOptimizeElement);
            }

            log('SDK initialized');
            return this;
        },

        // Manual tracking
        track(eventName, componentId, properties) {
            EventTracker.track(eventName, componentId, properties);
        },

        // A/B Testing Scoring
        async scoreInteraction(componentId, interactionType, variant = null) {
            const ids = UserManager.getIds();
            const activeVariant = variant || document.querySelector(`[component-id="${componentId}"]`)?.getAttribute('data-active-variant') || 'A';

            try {
                const response = await fetch(`${CONFIG.apiBaseUrl}/api/scoring/interaction`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': CONFIG.apiKey
                    },
                    body: JSON.stringify({
                        user_id: ids.user_id,
                        component_id: componentId,
                        interaction_type: interactionType,
                        variant: activeVariant,
                        properties: {}
                    })
                });

                const result = await response.json();
                log('Interaction scored:', componentId, interactionType, result);

                // Emit event if regeneration triggered
                if (result.should_regenerate) {
                    window.dispatchEvent(new CustomEvent('htmlai:regenerate', {
                        detail: {
                            componentId,
                            variant: result.regenerate_variant,
                            scoreDiff: result.score_difference
                        }
                    }));
                }

                return result;
            } catch (err) {
                console.error('[html.ai] Score tracking failed:', err);
                return null;
            }
        },

        // Reward a component (triggers scoring + potential regeneration)
        async rewardComponent(componentId, reward = 1, interactionType = 'conversion', contextHtml = '') {
            const ids = UserManager.getIds();
            const element = document.querySelector(`[component-id="${componentId}"]`);
            const activeVariant = element?.getAttribute('data-active-variant') || 'A';

            try {
                const response = await fetch(`${CONFIG.apiBaseUrl}/api/component/reward`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': CONFIG.apiKey
                    },
                    body: JSON.stringify({
                        user_id: ids.user_id,
                        component_id: componentId,
                        variant: activeVariant,
                        reward: reward,
                        context_html: contextHtml || element?.outerHTML || '',
                        interaction_type: interactionType
                    })
                });

                const result = await response.json();
                log('Component rewarded:', componentId, result);

                return result;
            } catch (err) {
                console.error('[html.ai] Reward failed:', err);
                return null;
            }
        },

        // Get component with A/B variant
        async getComponent(componentId, html, contextHtml = '') {
            const ids = UserManager.getIds();

            try {
                const response = await fetch(`${CONFIG.apiBaseUrl}/api/component/generate`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': CONFIG.apiKey
                    },
                    body: JSON.stringify({
                        user_id: ids.user_id,
                        component_id: componentId,
                        changing_html: html,
                        context_html: contextHtml
                    })
                });

                const result = await response.json();
                log('Component generated:', componentId, result.variant);

                return result;
            } catch (err) {
                console.error('[html.ai] Component generation failed:', err);
                return { html, variant: 'A', status: 'fallback' };
            }
        },

        // Get user IDs
        getUser() {
            return UserManager.getIds();
        },

        // Callback when cross-site sync completes
        onSync(callback) {
            SyncManager.onSync(callback);
        },

        // Force flush events
        flush() {
            return EventTracker.flush();
        }
    };

    // ========================================
    // Auto-initialize
    // ========================================
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => HtmlAI.init());
    } else {
        HtmlAI.init();
    }

    // Expose globally
    window.HtmlAI = HtmlAI;

})(window, document);
