/**
 * Web Components SDK for Adaptive Identity Engine
 *
 * Usage:
 * ```html
 * <script src="ai-optimize.js"></script>
 *
 * <ai-optimize
 *   experiment-id="hero-section"
 *   component-type="hero"
 *   goal="conversion">
 *   <div class="hero">
 *     <h1>Original Headline</h1>
 *     <button>Shop Now</button>
 *   </div>
 * </ai-optimize>
 * ```
 */

(function() {
  'use strict';

  // Configuration
  const CONFIG = {
    apiBaseUrl: 'http://localhost:8000',
    userIdKey: 'adaptive_identity_uid',
    sessionIdKey: 'adaptive_identity_session',
    cookieMaxAgeDays: 365,
    eventBatchSize: 10,
    eventFlushInterval: 5000
  };

  // Cookie utilities
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
      document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
    }
  };

  // UUID generator
  function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  // User ID manager
  const UserIdManager = {
    getOrCreateUserId() {
      let userId = CookieUtils.get(CONFIG.userIdKey);
      if (!userId) {
        userId = generateUUID();
        CookieUtils.set(CONFIG.userIdKey, userId);
      }
      return userId;
    },

    getUserId() {
      return CookieUtils.get(CONFIG.userIdKey) || this.getOrCreateUserId();
    }
  };

  // Session manager
  const SessionManager = {
    getOrCreateSessionId() {
      let sessionId = sessionStorage.getItem(CONFIG.sessionIdKey);
      if (!sessionId) {
        sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        sessionStorage.setItem(CONFIG.sessionIdKey, sessionId);
      }
      return sessionId;
    }
  };

  // Event queue for batching
  class EventQueue {
    constructor() {
      this.events = [];
      this.flushTimer = null;
    }

    add(event) {
      this.events.push({
        ...event,
        timestamp: new Date().toISOString()
      });

      if (this.events.length >= CONFIG.eventBatchSize) {
        this.flush();
      } else if (!this.flushTimer) {
        this.flushTimer = setTimeout(() => this.flush(), CONFIG.eventFlushInterval);
      }
    }

    async flush() {
      if (this.flushTimer) {
        clearTimeout(this.flushTimer);
        this.flushTimer = null;
      }

      if (this.events.length === 0) return;

      const eventsToSend = [...this.events];
      this.events = [];

      try {
        await fetch(`${CONFIG.apiBaseUrl}/api/v2/track/events`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: UserIdManager.getUserId(),
            session_id: SessionManager.getOrCreateSessionId(),
            events: eventsToSend
          })
        });
      } catch (error) {
        // Re-queue events on failure
        this.events.unshift(...eventsToSend);
        console.error('[AdaptiveIdentity] Failed to flush events:', error);
      }
    }
  }

  const eventQueue = new EventQueue();

  // Flush events before page unload
  window.addEventListener('beforeunload', () => eventQueue.flush());
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      eventQueue.flush();
    }
  });

  /**
   * <ai-optimize> Custom Element
   *
   * Attributes:
   * - experiment-id: Unique identifier for this experiment
   * - component-type: Type of component (hero, product_card, cta, etc.)
   * - goal: Optimization goal (conversion, engagement, retention)
   * - api-url: Override API base URL
   */
  class AIOptimizeElement extends HTMLElement {
    static get observedAttributes() {
      return ['experiment-id', 'component-type', 'goal', 'api-url'];
    }

    constructor() {
      super();
      this.originalContent = '';
      this.variantId = null;
      this.identityState = null;
      this.isControl = false;
      this.mountTime = Date.now();
      this.intersectionObserver = null;
      this.isVisible = false;
    }

    connectedCallback() {
      // Store original content
      this.originalContent = this.innerHTML;

      // Show loading state
      this.classList.add('ai-optimize-loading');

      // Fetch variant
      this.fetchVariant();

      // Set up visibility tracking
      this.setupVisibilityTracking();

      // Set up interaction tracking
      this.setupInteractionTracking();
    }

    disconnectedCallback() {
      // Track time on component
      const timeSpent = (Date.now() - this.mountTime) / 1000;
      this.trackEvent('time_on_component', { time_seconds: timeSpent });

      // Clean up observer
      if (this.intersectionObserver) {
        this.intersectionObserver.disconnect();
      }

      // Flush any pending events
      eventQueue.flush();
    }

    attributeChangedCallback(name, oldValue, newValue) {
      if (oldValue !== newValue && this.isConnected) {
        this.fetchVariant();
      }
    }

    get experimentId() {
      return this.getAttribute('experiment-id') || 'default';
    }

    get componentType() {
      return this.getAttribute('component-type') || 'generic';
    }

    get goal() {
      return this.getAttribute('goal') || 'conversion';
    }

    get apiUrl() {
      return this.getAttribute('api-url') || CONFIG.apiBaseUrl;
    }

    async fetchVariant() {
      try {
        const response = await fetch(`${this.apiUrl}/api/v2/generate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: UserIdManager.getUserId(),
            session_id: SessionManager.getOrCreateSessionId(),
            experiment_id: this.experimentId,
            original_content: this.originalContent,
            component_type: this.componentType,
            goal: this.goal,
            platform: 'web-component',
            context: this.getContext()
          })
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        this.variantId = data.variant_id;
        this.identityState = data.identity_state;
        this.isControl = data.is_control;

        // Update content with variant
        this.innerHTML = data.generated_content || this.originalContent;

        // Remove loading state, add loaded state
        this.classList.remove('ai-optimize-loading');
        this.classList.add('ai-optimize-loaded');

        // Track variant shown
        this.trackEvent('variant_shown', {
          variant_id: this.variantId,
          identity_state: this.identityState,
          is_control: this.isControl,
          confidence: data.confidence
        });

        // Dispatch custom event
        this.dispatchEvent(new CustomEvent('variant-loaded', {
          bubbles: true,
          detail: {
            variantId: this.variantId,
            identityState: this.identityState,
            isControl: this.isControl,
            confidence: data.confidence
          }
        }));

      } catch (error) {
        console.error('[AIOptimize] Failed to fetch variant:', error);
        this.classList.remove('ai-optimize-loading');
        this.classList.add('ai-optimize-error');

        // Keep original content on error
        this.innerHTML = this.originalContent;

        this.dispatchEvent(new CustomEvent('variant-error', {
          bubbles: true,
          detail: { error }
        }));
      }
    }

    getContext() {
      return {
        viewport_width: window.innerWidth,
        viewport_height: window.innerHeight,
        device_pixel_ratio: window.devicePixelRatio,
        user_agent: navigator.userAgent,
        referrer: document.referrer,
        url: window.location.href
      };
    }

    setupVisibilityTracking() {
      this.intersectionObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting && !this.isVisible) {
              this.isVisible = true;
              this.trackEvent('component_viewed', {
                visibility_ratio: entry.intersectionRatio
              });
            } else if (!entry.isIntersecting && this.isVisible) {
              this.isVisible = false;
              this.trackEvent('component_hidden', {
                time_visible: (Date.now() - this.mountTime) / 1000
              });
            }
          });
        },
        { threshold: [0, 0.25, 0.5, 0.75, 1.0] }
      );

      this.intersectionObserver.observe(this);
    }

    setupInteractionTracking() {
      // Click tracking
      this.addEventListener('click', (e) => {
        this.trackEvent('click', {
          target_tag: e.target.tagName,
          target_class: e.target.className,
          target_id: e.target.id,
          x: e.offsetX,
          y: e.offsetY
        });
      });

      // Mouse enter/leave for engagement
      this.addEventListener('mouseenter', () => {
        this.trackEvent('mouse_enter');
      });

      this.addEventListener('mouseleave', () => {
        this.trackEvent('mouse_leave');
      });
    }

    trackEvent(eventName, properties = {}) {
      eventQueue.add({
        event_name: eventName,
        component_id: this.experimentId,
        properties: {
          ...properties,
          variant_id: this.variantId,
          identity_state: this.identityState,
          is_control: this.isControl
        }
      });
    }

    /**
     * Track a conversion event
     * @param {string} conversionType - Type of conversion (e.g., 'primary', 'add_to_cart')
     * @param {number} value - Optional monetary value
     */
    trackConversion(conversionType = 'primary', value = null) {
      if (!this.variantId) {
        console.warn('[AIOptimize] Cannot track conversion: no variant loaded');
        return;
      }

      fetch(`${this.apiUrl}/api/v2/track/conversion`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: UserIdManager.getUserId(),
          session_id: SessionManager.getOrCreateSessionId(),
          experiment_id: this.experimentId,
          variant_id: this.variantId,
          conversion_type: conversionType,
          value
        })
      }).catch((error) => {
        console.error('[AIOptimize] Failed to track conversion:', error);
      });

      // Dispatch custom event
      this.dispatchEvent(new CustomEvent('conversion', {
        bubbles: true,
        detail: {
          experimentId: this.experimentId,
          variantId: this.variantId,
          conversionType,
          value
        }
      }));
    }

    /**
     * Force refresh the variant
     */
    refresh() {
      this.fetchVariant();
    }
  }

  // Register custom element
  customElements.define('ai-optimize', AIOptimizeElement);

  // Expose global API
  window.AdaptiveIdentity = {
    config: CONFIG,
    getUserId: () => UserIdManager.getUserId(),
    getSessionId: () => SessionManager.getOrCreateSessionId(),

    trackEvent(eventName, componentId = null, properties = {}) {
      eventQueue.add({
        event_name: eventName,
        component_id: componentId,
        properties
      });
    },

    trackConversion(experimentId, variantId, conversionType = 'primary', value = null) {
      return fetch(`${CONFIG.apiBaseUrl}/api/v2/track/conversion`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: UserIdManager.getUserId(),
          session_id: SessionManager.getOrCreateSessionId(),
          experiment_id: experimentId,
          variant_id: variantId,
          conversion_type: conversionType,
          value
        })
      });
    },

    trackPageView(pageName, properties = {}) {
      eventQueue.add({
        event_name: 'page_viewed',
        component_id: null,
        properties: {
          ...properties,
          page_name: pageName,
          url: window.location.href,
          referrer: document.referrer
        }
      });
    },

    setApiUrl(url) {
      CONFIG.apiBaseUrl = url;
    },

    flushEvents() {
      return eventQueue.flush();
    }
  };

  // Auto-track page views
  window.AdaptiveIdentity.trackPageView(document.title);

  // Track page visibility changes
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
      window.AdaptiveIdentity.trackEvent('page_visible');
    } else {
      window.AdaptiveIdentity.trackEvent('page_hidden');
    }
  });

  console.log('[AdaptiveIdentity] Web Components SDK loaded');
})();
