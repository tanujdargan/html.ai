/**
 * Adaptive Identity Engine - Client SDK
 *
 * Plug-and-play script for dynamic UI personalization
 *
 * Usage:
 * <script src="https://cdn.adaptive-identity.ai/identity.js"></script>
 * <div data-identity-component="hero" data-goal="conversion" data-variants="3">
 *   Your content here
 * </div>
 */

(function() {
  'use strict';

  // Configuration
  const CONFIG = {
    apiBaseUrl: 'http://localhost:8000',  // Change in production
    sessionKey: 'adaptive_identity_session',
    debugMode: true  // Set to false in production
  };

  // ============================================================================
  // Session Management
  // ============================================================================

  class SessionManager {
    constructor() {
      this.sessionId = this.getOrCreateSession();
      this.userId = null;
    }

    getOrCreateSession() {
      // Check for existing session in cookie/localStorage
      let sessionId = localStorage.getItem(CONFIG.sessionKey);

      if (!sessionId) {
        sessionId = this.generateSessionId();
        localStorage.setItem(CONFIG.sessionKey, sessionId);
        this.createSessionOnServer(sessionId);
      }

      return sessionId;
    }

    generateSessionId() {
      return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    async createSessionOnServer(sessionId) {
      try {
        const response = await fetch(`${CONFIG.apiBaseUrl}/api/session/create`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });

        if (CONFIG.debugMode) {
          console.log('[Adaptive Identity] Session created:', sessionId);
        }
      } catch (error) {
        console.error('[Adaptive Identity] Failed to create session:', error);
      }
    }

    setUserId(userId) {
      this.userId = userId;
    }
  }

  // ============================================================================
  // Event Tracker
  // ============================================================================

  class EventTracker {
    constructor(sessionManager) {
      this.session = sessionManager;
      this.componentObservers = new Map();
    }

    /**
     * Track an event to the backend
     */
    async track(eventName, componentId = null, properties = {}) {
      const eventData = {
        event_name: eventName,
        session_id: this.session.sessionId,
        user_id: this.session.userId,
        component_id: componentId,
        properties: properties
      };

      try {
        const response = await fetch(`${CONFIG.apiBaseUrl}/api/events/track`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(eventData)
        });

        if (CONFIG.debugMode) {
          console.log('[Adaptive Identity] Event tracked:', eventName, componentId);
        }

        return await response.json();
      } catch (error) {
        console.error('[Adaptive Identity] Failed to track event:', error);
      }
    }

    /**
     * Set up automatic event tracking for a component
     */
    observeComponent(element, componentId) {
      // Track component viewed
      this.track('component_viewed', componentId, {
        component_type: element.dataset.identityComponent
      });

      // Track time on component
      const startTime = Date.now();

      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (!entry.isIntersecting && entry.target.dataset.tracked !== 'true') {
            const timeSeconds = (Date.now() - startTime) / 1000;
            this.track('time_on_component', componentId, {
              time_seconds: timeSeconds
            });
            entry.target.dataset.tracked = 'true';
          }
        });
      }, { threshold: 0.5 });

      observer.observe(element);
      this.componentObservers.set(componentId, observer);

      // Track clicks within component
      element.addEventListener('click', (e) => {
        this.track('click', componentId, {
          element: e.target.tagName,
          text: e.target.textContent.substring(0, 50)
        });
      });

      // Track scroll depth
      this.trackScrollDepth(element, componentId);
    }

    trackScrollDepth(element, componentId) {
      let maxScrollDepth = 0;

      window.addEventListener('scroll', () => {
        const rect = element.getBoundingClientRect();
        const viewportHeight = window.innerHeight;

        if (rect.top < viewportHeight && rect.bottom > 0) {
          const visibleHeight = Math.min(rect.bottom, viewportHeight) - Math.max(rect.top, 0);
          const scrollDepth = visibleHeight / rect.height;

          if (scrollDepth > maxScrollDepth) {
            maxScrollDepth = scrollDepth;

            if (maxScrollDepth > 0.25 && maxScrollDepth < 0.3) {
              this.track('scroll_depth_reached', componentId, { depth: 0.25 });
            } else if (maxScrollDepth > 0.5 && maxScrollDepth < 0.55) {
              this.track('scroll_depth_reached', componentId, { depth: 0.5 });
            } else if (maxScrollDepth > 0.75 && maxScrollDepth < 0.8) {
              this.track('scroll_depth_reached', componentId, { depth: 0.75 });
            }
          }
        }
      }, { passive: true });
    }
  }

  // ============================================================================
  // Variant Manager
  // ============================================================================

  class VariantManager {
    constructor(sessionManager, eventTracker) {
      this.session = sessionManager;
      this.tracker = eventTracker;
    }

    /**
     * Get and apply personalized variant from multi-agent system
     */
    async applyVariant(element, componentId) {
      try {
        const response = await fetch(`${CONFIG.apiBaseUrl}/api/variants/get`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: this.session.sessionId,
            component_id: componentId,
            user_id: this.session.userId
          })
        });

        const data = await response.json();

        if (CONFIG.debugMode) {
          console.log('[Adaptive Identity] Variant received:', data);
          console.log('[Adaptive Identity] Agent Communication Log:');
          data.audit_log.forEach(log => console.log('  ' + log));
        }

        // Apply variant to element
        this.renderVariant(element, data.content, data.variant_id);

        // Track variant shown
        await this.tracker.track('variant_shown', componentId, {
          variant_id: data.variant_id,
          identity_state: data.identity_state,
          confidence: data.confidence
        });

        // Store for dashboard
        if (CONFIG.debugMode) {
          this.showDebugPanel(data);
        }

        return data;

      } catch (error) {
        console.error('[Adaptive Identity] Failed to get variant:', error);
        // Keep original content on error
      }
    }

    /**
     * Render variant content into component
     */
    renderVariant(element, content, variantId) {
      element.dataset.variantId = variantId;

      // Update headline if exists
      const headline = element.querySelector('h1, h2, .headline');
      if (headline && content.headline) {
        headline.textContent = content.headline;
        headline.classList.add('variant-updated');
      }

      // Update subheadline
      const subheadline = element.querySelector('p, .subheadline');
      if (subheadline && content.subheadline) {
        subheadline.textContent = content.subheadline;
        subheadline.classList.add('variant-updated');
      }

      // Update CTA
      const cta = element.querySelector('button, .cta, a.button');
      if (cta && content.cta_text) {
        cta.textContent = content.cta_text;
        cta.classList.add('variant-updated');
      }

      // Add urgency indicator if specified
      if (content.urgency === 'high') {
        element.classList.add('urgency-high');
      }
    }

    /**
     * Show debug panel with agent communication
     */
    showDebugPanel(data) {
      let panel = document.getElementById('adaptive-identity-debug');

      if (!panel) {
        panel = document.createElement('div');
        panel.id = 'adaptive-identity-debug';
        panel.style.cssText = `
          position: fixed;
          bottom: 20px;
          right: 20px;
          width: 400px;
          max-height: 600px;
          overflow-y: auto;
          background: #1a1a1a;
          color: #fff;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 4px 20px rgba(0,0,0,0.3);
          font-family: monospace;
          font-size: 12px;
          z-index: 10000;
        `;
        document.body.appendChild(panel);
      }

      panel.innerHTML = `
        <h3 style="margin-top: 0;">🤖 Adaptive Identity Engine</h3>
        <div style="margin: 10px 0;">
          <strong>Identity:</strong> ${data.identity_state || 'N/A'}<br>
          <strong>Confidence:</strong> ${(data.confidence * 100).toFixed(0)}%<br>
          <strong>Variant:</strong> ${data.variant_id}
        </div>
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #444;">
          <strong>Agent Communication:</strong>
          <div style="margin-top: 10px; font-size: 11px; line-height: 1.5;">
            ${data.audit_log.map(log => `<div style="margin: 5px 0; color: #4ade80;">${log}</div>`).join('')}
          </div>
        </div>
      `;
    }
  }

  // ============================================================================
  // Main Identity Engine
  // ============================================================================

  class AdaptiveIdentityEngine {
    constructor() {
      this.sessionManager = new SessionManager();
      this.eventTracker = new EventTracker(this.sessionManager);
      this.variantManager = new VariantManager(this.sessionManager, this.eventTracker);
      this.initialized = false;
    }

    async init() {
      if (this.initialized) return;

      console.log('[Adaptive Identity] Initializing...');

      // Track page view
      await this.eventTracker.track('page_viewed', null, {
        url: window.location.href,
        referrer: document.referrer
      });

      // Find all marked components
      const components = document.querySelectorAll('[data-identity-component]');

      for (const element of components) {
        const componentId = element.dataset.identityComponent;

        // Start tracking this component
        this.eventTracker.observeComponent(element, componentId);

        // Get personalized variant
        await this.variantManager.applyVariant(element, componentId);
      }

      this.initialized = true;
      console.log('[Adaptive Identity] Initialized with', components.length, 'components');
    }

    /**
     * Public API for manual event tracking
     */
    track(eventName, properties = {}) {
      return this.eventTracker.track(eventName, null, properties);
    }

    /**
     * Set user ID for cross-session tracking (if opted in)
     */
    identify(userId) {
      this.sessionManager.setUserId(userId);
    }
  }

  // ============================================================================
  // Auto-initialize
  // ============================================================================

  // Create global instance
  window.AdaptiveIdentity = new AdaptiveIdentityEngine();

  // Auto-initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      window.AdaptiveIdentity.init();
    });
  } else {
    window.AdaptiveIdentity.init();
  }

})();
