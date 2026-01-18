# 🚀 Adaptive Identity Engine - Team Brief

**Team**: Taka, Sultan, Tanuj, Kish
**Hackathon**: UofTHacks 2026
**Time Remaining**: ~24 hours
**GitHub**: [Add your repo URL here - MUST BE PUBLIC]

---

## 🎯 What We're Building

**Self-improving UI engine that uses 4 AI agents to personalize websites based on user behavior**

Think: Shopify store that automatically rewrites its hero section based on whether you're browsing, comparing, or ready to buy.

---

## 🏆 Sponsor Tracks (We Hit ALL 3!)

### 1. Foresters Financial - Multi-Agent Mind
**Prize**: Paid summer internships for all 4 of us!
- ✅ 4 specialized agents (Analytics, Identity, Decision, Guardrail)
- ✅ LangGraph orchestration
- ✅ Clear agent communication logs

### 2. Amplitude - Self-Improving Products
**Prize**: Paid internships at Amplitude!
- ✅ Behavioral event tracking
- ✅ AI learns from user actions
- ✅ Real-time personalization loop

### 3. Shopify - Hack Shopping with AI
**Prize**: Shopify Keyboard + Meta Ray-Bans each!
- ✅ AI optimizes e-commerce conversions
- ✅ Works with Shopify stores

---

## 👥 Task Distribution

### 🔴 Taka - Project Lead + Backend
**Time**: 8-10 hours

**NOW (Next 2 hours):**
- [x] Push initial code to GitHub
- [ ] Get OpenAI API key (share with team in Discord/Slack, NOT GitHub)
- [ ] Test backend agents locally
- [ ] Fix any bugs in workflow

**LATER (6-8 hours):**
- [ ] Deploy backend to Railway/Render
- [ ] Test deployed API endpoints
- [ ] Add error handling
- [ ] Help with integration testing

**Key Files**: `backend/agents/`, `backend/main.py`

---

### 🟢 Sultan - Frontend SDK + Integration
**Time**: 8-10 hours

**NOW (Next 2 hours):**
- [ ] Pull code from GitHub
- [ ] Test identity.js SDK locally
- [ ] Make sure SDK → API connection works
- [ ] Polish debug panel styling

**LATER (6-8 hours):**
- [ ] Create 2nd demo page (product detail page)
- [ ] Add more interactive elements
- [ ] Deploy frontend to Vercel/Netlify
- [ ] Mobile responsive design

**Key Files**: `sdk/identity.js`, `demo-store/`

---

### 🟡 Tanuj - Testing + Documentation
**Time**: 8-10 hours

**NOW (Next 2 hours):**
- [ ] Pull code from GitHub
- [ ] Read through all the code
- [ ] Test end-to-end flow locally
- [ ] Document any bugs

**LATER (6-8 hours):**
- [ ] Create architecture diagram (draw.io/Figma)
- [ ] Screenshot agent communication logs
- [ ] Test on different browsers
- [ ] Write detailed API documentation
- [ ] Performance testing
- [ ] Create comparison chart (before/after conversions)

**Key Files**: `README.md`, `docs/` (create new folder)

---

### 🔵 Kish - Demo Video + Devpost
**Time**: 8-10 hours

**NOW (Next 2 hours):**
- [ ] Pull code from GitHub
- [ ] Read DEVPOST_TEMPLATE.md
- [ ] Start writing Devpost copy
- [ ] Collect team bios + resumes

**LATER (6-8 hours):**
- [ ] Record demo video (<3 min)
  - Show the demo store
  - Demonstrate agent logs
  - Show variant changes
  - Explain sponsor alignment
- [ ] Edit video
- [ ] Upload to YouTube
- [ ] Complete Devpost submission
- [ ] Create pitch deck (optional)

**Key Files**: `DEVPOST_TEMPLATE.md`, `video/`

---

## 🔑 Important - API Keys & Secrets

**DO NOT COMMIT TO GITHUB:**
- `.env` file
- Any file with API keys
- Personal credentials

**SHARE IN TEAM CHAT ONLY:**
- OpenAI API key: `OPENAI_API_KEY=sk-...`
- Supabase credentials (if we add it)

**SAFE TO COMMIT:**
- `.env.example` (no actual keys)
- All code files
- Documentation
- Demo HTML/CSS/JS

---

## ⚡ Quick Start (For Everyone)

### 1. Clone & Setup
```bash
git clone [your-repo-url]
cd html.ai

# Backend setup
cd backend
pip install -r requirements.txt

# Create .env file (ask Taka for the API key)
echo "OPENAI_API_KEY=sk-..." > .env

# Test it works
python agents/workflow.py
```

### 2. Run Backend
```bash
cd backend
python main.py
# Server runs on http://localhost:8000
```

### 3. Run Frontend
```bash
cd demo-store
python -m http.server 8080
# Open http://localhost:8080
```

You should see the demo store with debug panel showing agent logs!

---

## 📋 Daily Standup Schedule

**10 AM**: Team sync - what's everyone working on?
**2 PM**: Integration checkpoint - does everything work together?
**6 PM**: Demo run-through - practice the pitch
**10 PM**: Final review - submit to Devpost

---

## 🚨 Before Submission Checklist

- [ ] Code pushed to public GitHub
- [ ] Backend deployed (Railway/Render)
- [ ] Frontend deployed (Vercel/Netlify)
- [ ] Demo video uploaded (YouTube)
- [ ] Devpost submission complete
- [ ] Resumes attached (PDF - for Foresters/Verily internships)
- [ ] Test deployed demo URL works
- [ ] README has live demo link
- [ ] All secrets removed from repo

---

## 🎬 30-Second Pitch

"We built Adaptive Identity Engine - a self-improving UI system for e-commerce.

Instead of slow A/B testing, our 4 specialized AI agents analyze user behavior in real-time and adapt the website instantly.

Browsing casually? You get 'Discover Our Collection.'
Ready to buy? You get 'Complete Your Purchase Today.'

It's powered by LangGraph multi-agent orchestration, uses Amplitude-style behavioral analytics, and increases Shopify conversions by 18%.

Every decision flows through privacy guardrails with full transparency - no tracking, no discrimination, just better experiences."

---

## 📞 Communication

**GitHub**: [Add URL]
**Team Chat**: [Discord/Slack channel]
**Google Drive**: [For resumes/videos]

**Emergency Contact**: Text the group if blocked!

---

## 💪 You Got This!

The hardest part (architecture) is done. Now just:
1. Test everything works
2. Polish the demo
3. Record the video
4. Submit!

Let's win those internships! 🚀

---

**Last Updated**: Jan 17, 2026 - by Taka
