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
    apiBaseUrl: 'http://localhost:3000',  // htmlTag backend port
    sessionKey: 'ai_optimize_session',    // Standardized with SDK
    userIdCookie: 'ai_optimize_user_id',  // Standardized with SDK
    cookieMaxAgeDays: 365,  // 1 year persistence
    debugMode: true  // Set to false in production
  };

  // ============================================================================
  // Cookie Utilities
  // ============================================================================

  const CookieUtils = {
    /**
     * Set a cookie with optional expiration
     */
    set(name, value, days = CONFIG.cookieMaxAgeDays) {
      const date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      const expires = `expires=${date.toUTCString()}`;
      document.cookie = `${name}=${value};${expires};path=/;SameSite=Lax`;
    },

    /**
     * Get a cookie value by name
     */
    get(name) {
      const nameEQ = `${name}=`;
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.indexOf(nameEQ) === 0) {
          return cookie.substring(nameEQ.length);
        }
      }
      return null;
    },

    /**
     * Delete a cookie
     */
    delete(name) {
      document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
    }
  };

  // ============================================================================
  // User ID Management
  // ============================================================================

  const UserIdManager = {
    /**
     * Generate a UUID v4
     */
    generateUUID() {
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });
    },

    /**
     * Get or create a persistent user ID stored in cookies
     */
    getOrCreateUserId() {
      let userId = CookieUtils.get(CONFIG.userIdCookie);

      if (!userId) {
        userId = this.generateUUID();
        CookieUtils.set(CONFIG.userIdCookie, userId);

        if (CONFIG.debugMode) {
          console.log('[Adaptive Identity] New user ID generated:', userId);
        }
      } else if (CONFIG.debugMode) {
        console.log('[Adaptive Identity] Existing user ID found:', userId);
      }

      return userId;
    },

    /**
     * Get the current user ID (without creating new one)
     */
    getUserId() {
      return CookieUtils.get(CONFIG.userIdCookie);
    },

    /**
     * Reset the user ID (creates a new one)
     */
    resetUserId() {
      CookieUtils.delete(CONFIG.userIdCookie);
      return this.getOrCreateUserId();
    }
  };

  // ============================================================================
  // Session Management
  // ============================================================================

  class SessionManager {
    constructor() {
      this.userId = UserIdManager.getOrCreateUserId();  // Get persistent user ID from cookie
      this.sessionId = this.getOrCreateSession();
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
      // Session is created implicitly when first event is tracked
      // No separate endpoint needed - backend handles session creation
      if (CONFIG.debugMode) {
        console.log('[Adaptive Identity] Session initialized:', sessionId, 'for user:', this.userId);
      }
    }

    setUserId(userId) {
      this.userId = userId;
      // Also update the cookie
      CookieUtils.set(CONFIG.userIdCookie, userId);
    }

    getUserId() {
      return this.userId;
    }

    resetUserId() {
      this.userId = UserIdManager.resetUserId();
      return this.userId;
    }
  }

  // ============================================================================
  // Event Tracker (with batching to reduce API calls)
  // ============================================================================

  class EventTracker {
    constructor(sessionManager) {
      this.session = sessionManager;
      this.componentObservers = new Map();

      // Batching configuration
      this.eventQueue = [];
      this.batchInterval = 2000; // Send batch every 2 seconds
      this.maxQueueSize = 20; // Or when queue reaches 20 events
      this.batchTimer = null;

      // High-frequency event throttling (don't queue these too often)
      this.throttledEvents = new Map(); // eventName -> lastSentTime
      this.throttleIntervals = {
        'mouse_hesitation': 2000,      // Max once per 2 seconds
        'mouse_idle_start': 5000,      // Max once per 5 seconds
        'mouse_idle_end': 5000,
        'scroll_direction_change': 1000,
        'scroll_fast': 2000,
        'scroll_pause': 1000,
        'hover': 500,
        'hover_end': 500,
        'dead_click': 1000,
      };

      // Start batch processing
      this.startBatchProcessor();

      // Flush on page unload
      window.addEventListener('beforeunload', () => this.flushQueue());
    }

    startBatchProcessor() {
      this.batchTimer = setInterval(() => {
        this.flushQueue();
      }, this.batchInterval);
    }

    /**
     * Track an event (queued for batching)
     */
    async track(eventName, componentId = null, properties = {}) {
      // Check throttle for high-frequency events
      const throttleMs = this.throttleIntervals[eventName];
      if (throttleMs) {
        const lastSent = this.throttledEvents.get(eventName) || 0;
        const now = Date.now();
        if (now - lastSent < throttleMs) {
          // Skip this event, too soon
          return;
        }
        this.throttledEvents.set(eventName, now);
      }

      const eventData = {
        event_name: eventName,
        session_id: this.session.sessionId,
        user_id: this.session.userId,
        component_id: componentId,
        properties: properties,
        timestamp: new Date().toISOString()
      };

      // Add to queue
      this.eventQueue.push(eventData);

      if (CONFIG.debugMode) {
        console.log('[Adaptive Identity] Event queued:', eventName, `(queue size: ${this.eventQueue.length})`);
      }

      // Flush if queue is full
      if (this.eventQueue.length >= this.maxQueueSize) {
        this.flushQueue();
      }
    }

    /**
     * Send all queued events to backend
     */
    async flushQueue() {
      if (this.eventQueue.length === 0) return;

      const eventsToSend = [...this.eventQueue];
      this.eventQueue = [];

      try {
        // Send as batch
        const response = await fetch(`${CONFIG.apiBaseUrl}/api/events/batch`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: this.session.userId,
            session_id: this.session.sessionId,
            events: eventsToSend
          })
        });

        if (CONFIG.debugMode) {
          console.log(`[Adaptive Identity] Batch sent: ${eventsToSend.length} events`);
        }

        return await response.json();
      } catch (error) {
        // On error, put events back in queue (up to a limit)
        if (this.eventQueue.length < 50) {
          this.eventQueue = [...eventsToSend, ...this.eventQueue].slice(0, 50);
        }
        console.error('[Adaptive Identity] Failed to send batch:', error);
      }
    }

    /**
     * Track an event immediately (bypass batching for critical events)
     */
    async trackImmediate(eventName, componentId = null, properties = {}) {
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
          console.log('[Adaptive Identity] Event tracked (immediate):', eventName);
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
  // Advanced Behavior Tracker
  // ============================================================================

  class BehaviorTracker {
    constructor(eventTracker) {
      this.tracker = eventTracker;

      // Mouse tracking state
      this.lastMousePos = { x: 0, y: 0, time: Date.now() };
      this.mouseIdleTimeout = null;
      this.mouseIdleStart = null;
      this.mousePath = []; // Store recent mouse positions for velocity calc

      // Scroll tracking state
      this.lastScrollPos = 0;
      this.lastScrollTime = Date.now();
      this.scrollPauseTimeout = null;
      this.scrollDirectionChanges = 0;
      this.lastScrollDirection = null;

      // Click tracking state
      this.recentClicks = []; // For rage click detection
      this.clickHistory = [];

      // Hover tracking state
      this.hoverStart = null;
      this.hoveredElement = null;

      // Tab visibility
      this.tabHiddenStart = null;
      this.totalHiddenTime = 0;

      // Form tracking
      this.formFieldStart = null;
      this.currentField = null;
      this.fieldCorrections = {};

      // Timing
      this.pageLoadTime = Date.now();
      this.firstInteractionTime = null;
    }

    init() {
      this.initMouseTracking();
      this.initScrollTracking();
      this.initClickTracking();
      this.initHoverTracking();
      this.initVisibilityTracking();
      this.initFormTracking();
      this.initNavigationTracking();

      if (CONFIG.debugMode) {
        console.log('[Adaptive Identity] Advanced behavior tracking initialized');
      }
    }

    // ========================================
    // Mouse Tracking
    // ========================================
    initMouseTracking() {
      let throttleTimer = null;
      const THROTTLE_MS = 100; // Track mouse every 100ms max
      const IDLE_THRESHOLD_MS = 2000; // 2 seconds = idle
      const PATH_LENGTH = 10; // Keep last 10 positions for velocity

      document.addEventListener('mousemove', (e) => {
        if (throttleTimer) return;

        throttleTimer = setTimeout(() => {
          throttleTimer = null;

          const now = Date.now();
          const newPos = { x: e.clientX, y: e.clientY, time: now };

          // Calculate velocity
          if (this.lastMousePos.time) {
            const dx = newPos.x - this.lastMousePos.x;
            const dy = newPos.y - this.lastMousePos.y;
            const dt = (now - this.lastMousePos.time) / 1000; // seconds
            const distance = Math.sqrt(dx * dx + dy * dy);
            const velocity = dt > 0 ? distance / dt : 0;

            // Store in path for average velocity calculation
            this.mousePath.push({ ...newPos, velocity });
            if (this.mousePath.length > PATH_LENGTH) {
              this.mousePath.shift();
            }

            // Track significant velocity changes (hesitation signal)
            if (velocity < 50 && this.mousePath.length > 3) {
              const avgVelocity = this.mousePath.reduce((sum, p) => sum + (p.velocity || 0), 0) / this.mousePath.length;
              if (avgVelocity > 200 && velocity < 50) {
                // Sudden slowdown - possible hesitation
                this.tracker.track('mouse_hesitation', null, {
                  x: newPos.x,
                  y: newPos.y,
                  velocity_drop: avgVelocity - velocity,
                  element: this.getElementAtPoint(newPos.x, newPos.y)
                });
              }
            }
          }

          this.lastMousePos = newPos;

          // Reset idle timer
          if (this.mouseIdleTimeout) {
            clearTimeout(this.mouseIdleTimeout);

            // If we were idle, track how long
            if (this.mouseIdleStart) {
              const idleDuration = (now - this.mouseIdleStart) / 1000;
              if (idleDuration > 2) {
                this.tracker.track('mouse_idle_end', null, {
                  idle_seconds: idleDuration,
                  resume_position: { x: newPos.x, y: newPos.y }
                });
              }
              this.mouseIdleStart = null;
            }
          }

          this.mouseIdleTimeout = setTimeout(() => {
            this.mouseIdleStart = Date.now();
            this.tracker.track('mouse_idle_start', null, {
              last_position: { x: this.lastMousePos.x, y: this.lastMousePos.y },
              element: this.getElementAtPoint(this.lastMousePos.x, this.lastMousePos.y)
            });
          }, IDLE_THRESHOLD_MS);

          // Track first interaction
          if (!this.firstInteractionTime) {
            this.firstInteractionTime = now;
            this.tracker.track('first_interaction', null, {
              type: 'mousemove',
              time_to_interact_ms: now - this.pageLoadTime
            });
          }

        }, THROTTLE_MS);
      }, { passive: true });
    }

    // ========================================
    // Scroll Tracking (Enhanced)
    // ========================================
    initScrollTracking() {
      const PAUSE_THRESHOLD_MS = 500;
      let lastScrollTime = Date.now();

      window.addEventListener('scroll', () => {
        const now = Date.now();
        const currentPos = window.scrollY;
        const dt = (now - lastScrollTime) / 1000;
        const distance = Math.abs(currentPos - this.lastScrollPos);
        const velocity = dt > 0 ? distance / dt : 0;

        // Detect direction change (comparison/re-reading behavior)
        const direction = currentPos > this.lastScrollPos ? 'down' : 'up';
        if (this.lastScrollDirection && direction !== this.lastScrollDirection) {
          this.scrollDirectionChanges++;
          this.tracker.track('scroll_direction_change', null, {
            from: this.lastScrollDirection,
            to: direction,
            position: currentPos,
            total_changes: this.scrollDirectionChanges
          });
        }
        this.lastScrollDirection = direction;

        // Track scroll velocity (skimming vs reading)
        if (velocity > 2000) {
          this.tracker.track('scroll_fast', null, {
            velocity: velocity,
            direction: direction
          });
        }

        // Detect scroll pause (points of interest)
        if (this.scrollPauseTimeout) {
          clearTimeout(this.scrollPauseTimeout);
        }

        this.scrollPauseTimeout = setTimeout(() => {
          const pauseDuration = (Date.now() - now) / 1000;
          if (pauseDuration >= PAUSE_THRESHOLD_MS / 1000) {
            const viewportElements = this.getVisibleElements();
            this.tracker.track('scroll_pause', null, {
              position: currentPos,
              pause_seconds: pauseDuration,
              visible_elements: viewportElements.slice(0, 5) // Top 5 visible elements
            });
          }
        }, PAUSE_THRESHOLD_MS);

        this.lastScrollPos = currentPos;
        lastScrollTime = now;

      }, { passive: true });
    }

    // ========================================
    // Click Tracking (Rage clicks, dead clicks)
    // ========================================
    initClickTracking() {
      const RAGE_CLICK_THRESHOLD = 3; // 3+ clicks
      const RAGE_CLICK_WINDOW_MS = 1000; // within 1 second
      const RAGE_CLICK_RADIUS = 50; // within 50px

      document.addEventListener('click', (e) => {
        const now = Date.now();
        const click = {
          x: e.clientX,
          y: e.clientY,
          time: now,
          target: e.target.tagName,
          isInteractive: this.isInteractiveElement(e.target)
        };

        // Track first interaction
        if (!this.firstInteractionTime) {
          this.firstInteractionTime = now;
          this.tracker.track('first_interaction', null, {
            type: 'click',
            time_to_interact_ms: now - this.pageLoadTime
          });
        }

        // Dead click detection (click on non-interactive element)
        if (!click.isInteractive) {
          this.tracker.track('dead_click', null, {
            x: click.x,
            y: click.y,
            target: click.target,
            target_classes: e.target.className
          });
        }

        // Rage click detection
        this.recentClicks.push(click);

        // Remove old clicks outside the window
        this.recentClicks = this.recentClicks.filter(c => now - c.time < RAGE_CLICK_WINDOW_MS);

        // Check for rage clicks (multiple rapid clicks in same area)
        if (this.recentClicks.length >= RAGE_CLICK_THRESHOLD) {
          const firstClick = this.recentClicks[0];
          const allNearby = this.recentClicks.every(c => {
            const dx = c.x - firstClick.x;
            const dy = c.y - firstClick.y;
            return Math.sqrt(dx * dx + dy * dy) < RAGE_CLICK_RADIUS;
          });

          if (allNearby) {
            this.tracker.track('rage_click', null, {
              click_count: this.recentClicks.length,
              x: firstClick.x,
              y: firstClick.y,
              target: e.target.tagName,
              target_text: e.target.textContent?.substring(0, 50)
            });
            this.recentClicks = []; // Reset after detecting
          }
        }

        // Store in click history for pattern analysis
        this.clickHistory.push(click);
        if (this.clickHistory.length > 50) {
          this.clickHistory.shift();
        }

      }, { capture: true });

      // Track right clicks (power user behavior)
      document.addEventListener('contextmenu', (e) => {
        this.tracker.track('right_click', null, {
          x: e.clientX,
          y: e.clientY,
          target: e.target.tagName
        });
      });

      // Track double clicks
      document.addEventListener('dblclick', (e) => {
        this.tracker.track('double_click', null, {
          x: e.clientX,
          y: e.clientY,
          target: e.target.tagName,
          selected_text: window.getSelection()?.toString()?.substring(0, 100)
        });
      });
    }

    // ========================================
    // Hover Tracking
    // ========================================
    initHoverTracking() {
      const MIN_HOVER_MS = 500; // Only track hovers > 500ms

      // Track hover on interactive elements and product cards
      const trackableSelectors = [
        'button', 'a', '[data-identity-component]', '.product-card',
        'input', 'select', '[role="button"]', '.cta'
      ];

      document.addEventListener('mouseover', (e) => {
        const target = e.target.closest(trackableSelectors.join(','));
        if (!target || target === this.hoveredElement) return;

        // End previous hover
        if (this.hoveredElement && this.hoverStart) {
          const duration = Date.now() - this.hoverStart;
          if (duration >= MIN_HOVER_MS) {
            this.tracker.track('hover_end', null, {
              element: this.hoveredElement.tagName,
              element_id: this.hoveredElement.id,
              element_text: this.hoveredElement.textContent?.substring(0, 50),
              duration_ms: duration
            });
          }
        }

        this.hoveredElement = target;
        this.hoverStart = Date.now();

      }, { passive: true });

      document.addEventListener('mouseout', (e) => {
        const target = e.target.closest(trackableSelectors.join(','));
        if (!target || target !== this.hoveredElement) return;

        const duration = Date.now() - this.hoverStart;
        if (duration >= MIN_HOVER_MS) {
          this.tracker.track('hover', null, {
            element: target.tagName,
            element_id: target.id,
            element_classes: target.className,
            element_text: target.textContent?.substring(0, 50),
            duration_ms: duration,
            component_id: target.dataset?.identityComponent
          });
        }

        this.hoveredElement = null;
        this.hoverStart = null;

      }, { passive: true });
    }

    // ========================================
    // Tab Visibility Tracking
    // ========================================
    initVisibilityTracking() {
      document.addEventListener('visibilitychange', () => {
        const now = Date.now();

        if (document.hidden) {
          this.tabHiddenStart = now;
          this.tracker.track('tab_hidden', null, {
            time_on_page_before_hide_ms: now - this.pageLoadTime
          });
        } else {
          if (this.tabHiddenStart) {
            const hiddenDuration = now - this.tabHiddenStart;
            this.totalHiddenTime += hiddenDuration;
            this.tracker.track('tab_visible', null, {
              hidden_duration_ms: hiddenDuration,
              total_hidden_time_ms: this.totalHiddenTime
            });
            this.tabHiddenStart = null;
          }
        }
      });

      // Track window blur/focus (more granular than visibility)
      window.addEventListener('blur', () => {
        this.tracker.track('window_blur', null, {
          time_on_page_ms: Date.now() - this.pageLoadTime
        });
      });

      window.addEventListener('focus', () => {
        this.tracker.track('window_focus', null, {
          time_on_page_ms: Date.now() - this.pageLoadTime
        });
      });
    }

    // ========================================
    // Form Interaction Tracking
    // ========================================
    initFormTracking() {
      // Track field focus
      document.addEventListener('focusin', (e) => {
        if (!this.isFormField(e.target)) return;

        this.currentField = e.target;
        this.formFieldStart = Date.now();
        this.fieldCorrections[e.target.name || e.target.id] = 0;

        this.tracker.track('field_focus', null, {
          field_name: e.target.name || e.target.id,
          field_type: e.target.type,
          field_placeholder: e.target.placeholder
        });
      });

      // Track field blur
      document.addEventListener('focusout', (e) => {
        if (!this.isFormField(e.target) || e.target !== this.currentField) return;

        const duration = Date.now() - this.formFieldStart;
        const fieldName = e.target.name || e.target.id;

        this.tracker.track('field_blur', null, {
          field_name: fieldName,
          field_type: e.target.type,
          duration_ms: duration,
          corrections: this.fieldCorrections[fieldName] || 0,
          has_value: !!e.target.value
        });

        this.currentField = null;
      });

      // Track corrections (backspace/delete)
      document.addEventListener('keydown', (e) => {
        if (!this.isFormField(e.target)) return;

        if (e.key === 'Backspace' || e.key === 'Delete') {
          const fieldName = e.target.name || e.target.id;
          this.fieldCorrections[fieldName] = (this.fieldCorrections[fieldName] || 0) + 1;
        }
      });

      // Track copy/paste
      document.addEventListener('paste', (e) => {
        if (!this.isFormField(e.target)) return;

        this.tracker.track('field_paste', null, {
          field_name: e.target.name || e.target.id,
          field_type: e.target.type
        });
      });

      // Track form submission
      document.addEventListener('submit', (e) => {
        this.tracker.track('form_submit', null, {
          form_id: e.target.id,
          form_action: e.target.action,
          field_count: e.target.elements.length
        });
      });
    }

    // ========================================
    // Navigation Tracking
    // ========================================
    initNavigationTracking() {
      // Track when user tries to leave
      window.addEventListener('beforeunload', () => {
        this.tracker.track('page_exit_intent', null, {
          time_on_page_ms: Date.now() - this.pageLoadTime,
          scroll_depth: this.getScrollDepthPercent(),
          total_clicks: this.clickHistory.length,
          tab_switches: this.totalHiddenTime > 0 ? Math.ceil(this.totalHiddenTime / 1000) : 0
        });
      });

      // Track external link clicks
      document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (!link) return;

        const href = link.getAttribute('href');
        if (href && (href.startsWith('http') && !href.includes(window.location.hostname))) {
          this.tracker.track('external_link_click', null, {
            href: href,
            link_text: link.textContent?.substring(0, 50)
          });
        }
      });

      // Track back button usage (popstate)
      window.addEventListener('popstate', () => {
        this.tracker.track('back_navigation', null, {
          current_url: window.location.href
        });
      });
    }

    // ========================================
    // Helper Methods
    // ========================================
    getElementAtPoint(x, y) {
      const el = document.elementFromPoint(x, y);
      if (!el) return null;
      return {
        tag: el.tagName,
        id: el.id,
        classes: el.className,
        text: el.textContent?.substring(0, 30)
      };
    }

    getVisibleElements() {
      const elements = [];
      document.querySelectorAll('[data-identity-component], .product-card, h1, h2, button').forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight && rect.bottom > 0) {
          elements.push({
            tag: el.tagName,
            id: el.id,
            component: el.dataset?.identityComponent
          });
        }
      });
      return elements;
    }

    isInteractiveElement(el) {
      const interactiveTags = ['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'];
      const interactiveRoles = ['button', 'link', 'checkbox', 'radio', 'tab'];

      return interactiveTags.includes(el.tagName) ||
             interactiveRoles.includes(el.getAttribute('role')) ||
             el.onclick !== null ||
             el.style.cursor === 'pointer' ||
             window.getComputedStyle(el).cursor === 'pointer';
    }

    isFormField(el) {
      return ['INPUT', 'TEXTAREA', 'SELECT'].includes(el.tagName);
    }

    getScrollDepthPercent() {
      const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
      return scrollHeight > 0 ? Math.round((window.scrollY / scrollHeight) * 100) : 0;
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
        const response = await fetch(`${CONFIG.apiBaseUrl}/api/optimize`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: this.session.userId,
            component_id: componentId,
            html: element.innerHTML.trim(),
            context_html: document.body.innerHTML.substring(0, 1000)
          })
        });

        if (!response.ok) {
          throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        if (CONFIG.debugMode) {
          console.log('[Adaptive Identity] Variant received:', data);
          if (data.audit_log && data.audit_log.length > 0) {
            console.log('[Adaptive Identity] Agent Communication Log:');
            data.audit_log.forEach(log => console.log('  ' + log));
          }
        }

        // Only apply if we got valid content
        if (data.content && data.variant_id) {
          // Apply variant to element
          this.renderVariant(element, data.content, data.variant_id);

          // Track variant shown (use immediate for important events)
          await this.tracker.trackImmediate('variant_shown', componentId, {
            variant_id: data.variant_id,
            identity_state: data.identity_state,
            confidence: data.confidence
          });
        }

        // Store for dashboard
        if (CONFIG.debugMode) {
          this.showDebugPanel(data);
        }

        return data;

      } catch (error) {
        console.error('[Adaptive Identity] Failed to get variant:', error);
        console.error('[Adaptive Identity] User ID:', this.session.userId);
        console.error('[Adaptive Identity] API URL:', CONFIG.apiBaseUrl);
        // Show error in debug panel
        if (CONFIG.debugMode) {
          this.showDebugPanel({
            identity_state: 'error',
            confidence: 0,
            variant_id: 'none',
            audit_log: [
              `Error: ${error.message}`,
              `User ID: ${this.session.userId}`,
              `API: ${CONFIG.apiBaseUrl}/api/optimize`,
              'Try: Clear browser cache and cookies, then refresh'
            ]
          });
        }
      }
    }

    /**
     * Render variant content into component
     */
    renderVariant(element, content, variantId) {
      element.dataset.variantId = variantId;

      // Update badge
      const badge = element.querySelector('.hero-badge');
      if (badge) {
        const identityLabel = variantId.split('_')[1] || 'default';
        badge.textContent = identityLabel.toUpperCase();
      }

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

      // Remove all existing variant classes
      element.classList.remove(
        'variant-confident',
        'variant-exploratory',
        'variant-overwhelmed',
        'variant-comparison',
        'variant-ready',
        'variant-cautious',
        'variant-impulse',
        'urgency-high'
      );

      // Apply variant-specific CSS class based on variantId
      if (variantId.includes('confident')) {
        element.classList.add('variant-confident');
      } else if (variantId.includes('exploratory')) {
        element.classList.add('variant-exploratory');
      } else if (variantId.includes('overwhelmed')) {
        element.classList.add('variant-overwhelmed');
      } else if (variantId.includes('comparison')) {
        element.classList.add('variant-comparison');
      } else if (variantId.includes('ready')) {
        element.classList.add('variant-ready');
      } else if (variantId.includes('cautious')) {
        element.classList.add('variant-cautious');
      } else if (variantId.includes('impulse')) {
        element.classList.add('variant-impulse');
      }

      // Add urgency indicator if specified
      if (content.urgency === 'high' || content.urgency === 'extreme') {
        element.classList.add('urgency-high');
      }

      console.log('[Adaptive Identity] Applied variant class:', variantId);
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

      const auditLogHtml = data.audit_log && data.audit_log.length > 0
        ? data.audit_log.map(log => `<div style="margin: 5px 0; color: #4ade80;">${log}</div>`).join('')
        : '<div style="color: #888;">No agent logs available</div>';

      panel.innerHTML = `
        <h3 style="margin-top: 0;">🤖 Adaptive Identity Engine</h3>
        <div style="margin: 10px 0;">
          <strong>Identity:</strong> ${data.identity_state || 'N/A'}<br>
          <strong>Confidence:</strong> ${((data.confidence || 0) * 100).toFixed(0)}%<br>
          <strong>Variant:</strong> ${data.variant_id || 'default'}
        </div>
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #444;">
          <strong>Agent Communication:</strong>
          <div style="margin-top: 10px; font-size: 11px; line-height: 1.5;">
            ${auditLogHtml}
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
      this.behaviorTracker = new BehaviorTracker(this.eventTracker);
      this.initialized = false;
    }

    async init() {
      if (this.initialized) return;

      console.log('[Adaptive Identity] Initializing...');

      // Initialize advanced behavior tracking
      this.behaviorTracker.init();

      // Track page view
      await this.eventTracker.track('page_viewed', null, {
        url: window.location.href,
        referrer: document.referrer
      });

      // Find all marked components
      this.components = document.querySelectorAll('[data-identity-component]');

      for (const element of this.components) {
        const componentId = element.dataset.identityComponent;

        // Start tracking this component
        this.eventTracker.observeComponent(element, componentId);

        // Get personalized variant
        await this.variantManager.applyVariant(element, componentId);
      }

      // Set up periodic refresh to update identity as user interacts
      this.startPeriodicRefresh();

      this.initialized = true;
      console.log('[Adaptive Identity] Initialized with', this.components.length, 'components');
    }

    /**
     * Periodically refresh variants based on accumulated behavior
     */
    startPeriodicRefresh() {
      const REFRESH_INTERVAL = 5000; // Refresh every 5 seconds

      setInterval(async () => {
        // Flush any pending events first
        await this.eventTracker.flushQueue();

        // Re-fetch variants for all components
        for (const element of this.components) {
          const componentId = element.dataset.identityComponent;
          await this.variantManager.applyVariant(element, componentId);
        }
      }, REFRESH_INTERVAL);

      console.log('[Adaptive Identity] Periodic refresh enabled (every 5s)');
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

    /**
     * Get the current persistent user ID (from cookie)
     */
    getUserId() {
      return this.sessionManager.getUserId();
    }

    /**
     * Get the current session ID
     */
    getSessionId() {
      return this.sessionManager.sessionId;
    }

    /**
     * Reset user ID (generates a new one)
     */
    resetUserId() {
      return this.sessionManager.resetUserId();
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
