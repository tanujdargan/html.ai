/**
 * React Hook for Adaptive Identity Engine
 *
 * Usage:
 * ```tsx
 * import { useAdaptiveUI } from '@adaptive-identity/react';
 *
 * function HeroSection() {
 *   const { content, isLoading, trackEvent } = useAdaptiveUI({
 *     experimentId: 'hero-cta-test',
 *     originalContent: '<div>Original Hero</div>',
 *     componentType: 'hero',
 *     goal: 'conversion'
 *   });
 *
 *   if (isLoading) return <Skeleton />;
 *
 *   return (
 *     <div
 *       dangerouslySetInnerHTML={{ __html: content }}
 *       onClick={() => trackEvent('click', { element: 'cta' })}
 *     />
 *   );
 * }
 * ```
 */

import { useState, useEffect, useCallback, useRef } from 'react';

interface AdaptiveUIConfig {
  apiBaseUrl?: string;
  experimentId: string;
  originalContent: string;
  componentType?: string;
  goal?: string;
  context?: Record<string, any>;
}

interface AdaptiveUIState {
  content: string;
  variantId: string | null;
  identityState: string | null;
  confidence: number;
  isLoading: boolean;
  isControl: boolean;
  error: Error | null;
}

interface EventProperties {
  [key: string]: any;
}

const DEFAULT_API_URL = 'http://localhost:8000';
const USER_ID_KEY = 'adaptive_identity_uid';
const SESSION_ID_KEY = 'adaptive_identity_session';

// UUID generator
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

// Get or create persistent user ID
function getUserId(): string {
  if (typeof window === 'undefined') return generateUUID();

  let userId = localStorage.getItem(USER_ID_KEY);
  if (!userId) {
    userId = generateUUID();
    localStorage.setItem(USER_ID_KEY, userId);
  }
  return userId;
}

// Get or create session ID
function getSessionId(): string {
  if (typeof window === 'undefined') return generateUUID();

  let sessionId = sessionStorage.getItem(SESSION_ID_KEY);
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem(SESSION_ID_KEY, sessionId);
  }
  return sessionId;
}

export function useAdaptiveUI(config: AdaptiveUIConfig) {
  const {
    apiBaseUrl = DEFAULT_API_URL,
    experimentId,
    originalContent,
    componentType = 'generic',
    goal = 'conversion',
    context = {}
  } = config;

  const [state, setState] = useState<AdaptiveUIState>({
    content: originalContent,
    variantId: null,
    identityState: null,
    confidence: 0,
    isLoading: true,
    isControl: false,
    error: null
  });

  const userIdRef = useRef<string>(getUserId());
  const sessionIdRef = useRef<string>(getSessionId());
  const mountTimeRef = useRef<number>(Date.now());

  // Fetch optimized variant
  useEffect(() => {
    async function fetchVariant() {
      try {
        const response = await fetch(`${apiBaseUrl}/api/v2/generate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: userIdRef.current,
            session_id: sessionIdRef.current,
            experiment_id: experimentId,
            original_content: originalContent,
            component_type: componentType,
            goal,
            platform: 'react',
            context
          })
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        setState({
          content: data.generated_content || originalContent,
          variantId: data.variant_id,
          identityState: data.identity_state,
          confidence: data.confidence,
          isLoading: false,
          isControl: data.is_control,
          error: null
        });
      } catch (error) {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: error as Error
        }));
      }
    }

    fetchVariant();
  }, [apiBaseUrl, experimentId, originalContent, componentType, goal]);

  // Track event
  const trackEvent = useCallback(
    async (eventName: string, properties: EventProperties = {}) => {
      try {
        await fetch(`${apiBaseUrl}/api/events/track`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            event_name: eventName,
            session_id: sessionIdRef.current,
            user_id: userIdRef.current,
            component_id: experimentId,
            properties: {
              ...properties,
              variant_id: state.variantId,
              identity_state: state.identityState
            }
          })
        });
      } catch (error) {
        console.error('[AdaptiveUI] Failed to track event:', error);
      }
    },
    [apiBaseUrl, experimentId, state.variantId, state.identityState]
  );

  // Track conversion
  const trackConversion = useCallback(
    async (conversionType: string = 'primary', value?: number) => {
      if (!state.variantId) return;

      try {
        await fetch(`${apiBaseUrl}/api/v2/track/conversion`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: userIdRef.current,
            session_id: sessionIdRef.current,
            experiment_id: experimentId,
            variant_id: state.variantId,
            conversion_type: conversionType,
            value
          })
        });
      } catch (error) {
        console.error('[AdaptiveUI] Failed to track conversion:', error);
      }
    },
    [apiBaseUrl, experimentId, state.variantId]
  );

  // Track time on component when unmounting
  useEffect(() => {
    return () => {
      const timeSpent = (Date.now() - mountTimeRef.current) / 1000;
      trackEvent('time_on_component', { time_seconds: timeSpent });
    };
  }, [trackEvent]);

  return {
    content: state.content,
    variantId: state.variantId,
    identityState: state.identityState,
    confidence: state.confidence,
    isLoading: state.isLoading,
    isControl: state.isControl,
    error: state.error,
    trackEvent,
    trackConversion,
    userId: userIdRef.current,
    sessionId: sessionIdRef.current
  };
}

// HOC for class components
export function withAdaptiveUI<P extends object>(
  WrappedComponent: React.ComponentType<P & ReturnType<typeof useAdaptiveUI>>,
  config: Omit<AdaptiveUIConfig, 'originalContent'> & { originalContent?: string }
) {
  return function AdaptiveUIWrapper(props: P & { originalContent?: string }) {
    const adaptiveUI = useAdaptiveUI({
      ...config,
      originalContent: props.originalContent || config.originalContent || ''
    });

    return <WrappedComponent {...props} {...adaptiveUI} />;
  };
}

export default useAdaptiveUI;
