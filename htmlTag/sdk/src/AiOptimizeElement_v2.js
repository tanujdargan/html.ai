// AiOptimizeElement_v2.js

// Cookie utilities
function setCookie(name, value, days = 365) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
    return null;
}

function generateUserId() {
    return 'user_' + Math.random().toString(36).substr(2, 16) + Date.now().toString(36);
}

// Get or create persistent user ID from cookie
function getOrCreateUserId() {
    let userId = getCookie('htmlai_user_id');
    if (!userId) {
        userId = generateUserId();
        setCookie('htmlai_user_id', userId);
        console.log('🆕 Created new user ID:', userId);
    } else {
        console.log('🔄 Found existing user ID:', userId);
    }
    return userId;
}

// Get global UID from cookie (set by sync iframe)
function getGlobalUid() {
    return getCookie('htmlai_guid');
}

// Set global UID cookie
function setGlobalUid(guid) {
    setCookie('htmlai_guid', guid);
}

// Expose utilities globally
window.HtmlAICookies = {
    getUserId: getOrCreateUserId,
    getGlobalUid: getGlobalUid,
    setGlobalUid: setGlobalUid,
    setCookie: setCookie,
    getCookie: getCookie
};

export class AiOpt extends HTMLElement {
    constructor() {
        super();
        this.originalHtml = this.innerHTML;
        this.optimized = false;
    }

    connectedCallback() {
        setTimeout(() => this.optimize(), 50);
    }

    async optimize() {
        if (this.optimized) return;

        // Get user ID from cookie (persistent across sessions)
        const userId = getOrCreateUserId();

        // Get global UID if available (cross-site identity)
        const globalUid = getGlobalUid();

        const contextHtml = document.documentElement.outerHTML;

        const payload = {
            user_id: userId,
            changingHtml: this.originalHtml,
            contextHtml: contextHtml,
            global_uid: globalUid || null
        };

        console.log("📤 Sending payload:", { user_id: userId, global_uid: globalUid });

        try {
            const response = await fetch("http://localhost:3000/tagAi", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
                credentials: 'include'
            });

            const data = await response.json();
            console.log("📥 Backend replied:", data);

            if (!response.ok) {
                console.warn("❌ Optimization failed:", data);
                return;
            }

            this.innerHTML = data.changingHtml;
            this.optimized = true;

            // Expose current variant globally and update debug panel
            window.currentVariant = data.variant;
            window.currentUserId = userId;

            const variantEl = document.getElementById('debug-variant');
            if (variantEl) {
                variantEl.textContent = data.variant || '--';
            }

            // Update user ID in debug panel if exists
            const userIdEl = document.getElementById('debug-uid');
            if (userIdEl) {
                userIdEl.textContent = userId;
            }

            // Also update the reward button's variant attribute
            const rewardBtn = document.getElementById('reward-btn');
            if (rewardBtn && data.variant) {
                rewardBtn.setAttribute('variant', data.variant);
            }

        } catch (err) {
            console.error("🔥 ERROR:", err);
        }
    }
}

customElements.define("ai-opt", AiOpt);
