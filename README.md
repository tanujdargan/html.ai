# 🚀 html.ai — Quick Start Guide 

This project lets developers wrap any part of their website in a **custom HTML tag** (`<ai-opt>`) that automatically sends its inner HTML to an AI backend for analysis, variant generation, and personalization.

This README explains:
- How to run everything
- Which ports matter
- What each teammate should work on

---

# 📂 Project Structure
html.ai/
│
├── htmlTag/
│   ├── sdk/
│   │   ├── src/
│   │   │   ├── AiOptimizeElement.js
│   │   │   ├── index.js
│   │   │   └── index.html
│   │
│   ├── aiBackend/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── server.py
│   │
│   └── Docker-compose.yml
│
└── aiusage.txt

---

# 🔌 Ports Overview

| Component | Port | Purpose |
|----------|------|---------|
| SDK Demo | 8080 | Frontend demo server |
| Backend  | 3000 | FastAPI that receives HTML + returns variants |
| MongoDB  | 27017 | Data store |

---

# 🐳 Running Backend

Make sure Docker Desktop is running, then inside:

```
html.ai/htmlTag
```

run:

```
docker compose up --build
```

If successful, you should see:

- **FastAPI backend** → running on `http://localhost:3000`
- **MongoDB** → running on port `27017`

To stop:

```
CTRL+C
docker compose down
```

---

# 🧪 Running the Frontend Demo (SDK Tester)

Open a second terminal and run:

```
cd html.ai/htmlTag/sdk/src
python3 -m http.server 8080
```

Visit:

```
http://localhost:8080
```

You should see the demo page with two `<ai-opt>` blocks.

Every time the page loads, each block sends its HTML to the backend at:

```
POST http://localhost:3000/log-html
```

Check Docker logs to confirm HTML is being captured.

---

# 🧩 How the Custom Tag Works

Developers wrap any part of their site:

```html
<ai-opt experiment="hero-cta">
    <button>Click Me</button>
</ai-opt>
```

Our SDK:

1. Extracts the inner HTML  
2. Sends it to the backend  
3. Awaits the returned variant  
4. Replaces the DOM dynamically

Example payload sent:

```json
{
  "experiment": "hero-cta",
  "html": "<button>Click Me</button>"
}
```

Backend replies with:

```json
{
  "html": "<button style='background:red'>Buy Now</button>"
}
```

DOM updates automatically.

---

# 🧠 Future AI Layer (Team Task #3)

Later, instead of returning static HTML, the backend will:

- Store variants in MongoDB  
- Use LLM agents to produce personalized variants  
- Track performance metrics  
- Evolve each component over time  

---

# 👥 Recommended Team Breakdown (4 Teammates)

| Person | Responsibilities |
|--------|------------------|
| **1: SDK Engineer** | Custom tag, DOM rendering, CDN packaging |
| **2: Backend Engineer** | FastAPI endpoints, Docker, routing |
| **3: AI/ML Engineer** | Variant generation, LLM logic, scoring |
| **4: Infra/Data Engineer** | Mongo models, data logging, analytics |

---

# 🧱 File Responsibilities

### **htmlTag/sdk/**
Everything frontend:
- `AiOptimizeElement.js` → defines `<ai-opt>`
- `index.js` → auto-registers custom element
- `index.html` → demo

### **htmlTag/aiBackend/**
Everything backend:
- `server.py` → FastAPI logic
- `requirements.txt` → dependencies
- `Dockerfile` → container image

### **htmlTag/Docker-compose.yml**
Orchestrates backend + MongoDB.

