# html.ai Vultr Deployment Guide

**Website (htmlai.tech) stays on Vercel**
**Backend services go on Vultr**

## Architecture

```
┌─────────────────────────────────────┐
│          Your Users                 │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌────────────┐    ┌─────────────────────────────┐
│  VERCEL    │    │         VULTR VPS           │
│            │    │                             │
│ htmlai.tech│    │  api.htmlai.tech            │
│ (website)  │    │  demo.htmlai.tech           │
│            │    │  dashboard.htmlai.tech      │
└────────────┘    │                             │
                  │  ┌─────┐ ┌──────┐ ┌──────┐  │
                  │  │Nginx│→│Engine│→│Mongo │  │
                  │  └─────┘ └──────┘ └──────┘  │
                  └─────────────────────────────┘
```

## Quick Start (10 minutes)

### Step 1: Create Vultr VPS

1. Go to [Vultr.com](https://my.vultr.com/deploy/) → **Deploy New Server**
2. Select:
   - **Type**: Cloud Compute (Shared CPU)
   - **Location**: New York or closest to your users
   - **Image**: Ubuntu 22.04 LTS x64
   - **Plan**: $12/mo (1 vCPU, 2GB RAM) — enough for demo
   - **SSH Keys**: Add your SSH key (or use password)
   - **Hostname**: `htmlai-backend`
3. Click **Deploy Now** and wait ~2 minutes
4. Copy the **IP address**

### Step 2: Configure DNS

Add these DNS records for **htmlai.tech** (only the subdomains, not the main domain):

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | api | YOUR_VULTR_IP | 300 |
| A | demo | YOUR_VULTR_IP | 300 |
| A | dashboard | YOUR_VULTR_IP | 300 |

**Note**: Leave `@` and `www` pointing to Vercel!

Wait 5-10 minutes for DNS to propagate. Test with:
```bash
ping api.htmlai.tech
```

### Step 3: SSH into Server

```bash
ssh root@YOUR_VULTR_IP
```

### Step 4: Run Deployment Script

```bash
# Clone and run setup
git clone https://github.com/tanujdargan/html.ai.git /opt/htmlai
cd /opt/htmlai/deploy
chmod +x setup.sh
./setup.sh
```

### Step 5: Add Your OpenAI API Key

```bash
nano /opt/htmlai/deploy/.env
```

Change:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Save (Ctrl+X, Y, Enter) and restart:
```bash
cd /opt/htmlai/deploy
docker-compose -f docker-compose.prod.yml restart engine
```

### Done!

Your services are now live:

| Service | URL |
|---------|-----|
| Website | https://htmlai.tech (Vercel) |
| API | https://api.htmlai.tech |
| Demo Store A | https://demo.htmlai.tech/demo-business-a.html |
| Demo Store B | https://demo.htmlai.tech/demo-business-b.html |
| Dashboard | https://dashboard.htmlai.tech |

---

## Useful Commands

### View Logs
```bash
cd /opt/htmlai/deploy
docker-compose -f docker-compose.prod.yml logs -f          # All services
docker-compose -f docker-compose.prod.yml logs -f engine   # Just API
docker-compose -f docker-compose.prod.yml logs -f nginx    # Just nginx
```

### Restart Services
```bash
cd /opt/htmlai/deploy
docker-compose -f docker-compose.prod.yml restart          # All
docker-compose -f docker-compose.prod.yml restart engine   # Just API
```

### Update Code
```bash
cd /opt/htmlai
git pull origin main
cd deploy
docker-compose -f docker-compose.prod.yml up -d --build
```

### Check Status
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Clear Database
```bash
docker exec -it htmlai-mongo mongosh --eval "use html_ai; db.dropDatabase();"
```

---

## Troubleshooting

### SSL Certificate Issues
```bash
# Check cert status
docker-compose -f docker-compose.prod.yml run --rm certbot certificates

# Force renewal
docker-compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal
docker-compose -f docker-compose.prod.yml restart nginx
```

### API Returns Errors
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs engine

# Check if OpenAI key is set
docker exec htmlai-engine env | grep OPENAI
```

### DNS Not Working
```bash
# Check if DNS propagated
dig api.htmlai.tech
nslookup api.htmlai.tech

# Should return your Vultr IP
```

### CORS Errors in Browser
The nginx config includes CORS headers. If you still get errors:
```bash
# Check nginx logs
docker-compose -f docker-compose.prod.yml logs nginx
```

---

## Cost Summary

| Service | Cost |
|---------|------|
| Vultr VPS (2GB) | $12/month |
| Domain (if needed) | ~$10/year |
| **Total** | **~$13/month** |

With $250 Vultr credits = **~20 months free!**

---

## Manual Deployment (if script fails)

### Install Docker
```bash
curl -fsSL https://get.docker.com | sh
systemctl enable docker && systemctl start docker
```

### Install Docker Compose
```bash
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Clone & Setup
```bash
git clone https://github.com/tanujdargan/html.ai.git /opt/htmlai
cd /opt/htmlai/deploy
mkdir -p certbot/conf certbot/www

# Create .env
echo "OPENAI_API_KEY=sk-your-key" > .env
```

### Update URLs
```bash
cd /opt/htmlai
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' htmlTag/demo-business-a.html
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' htmlTag/demo-business-b.html
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' htmlTag/admin-dashboard.html
sed -i 's|http://localhost:3001|https://api.htmlai.tech/analytics|g' htmlTag/admin-dashboard.html
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' htmlTag/sdk/src/AiOptimizeElement_v2.js
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' htmlTag/sdk/src/rewardbutton.js
```

### Get SSL Certs
```bash
cd /opt/htmlai/deploy

# Temporarily allow HTTP for cert generation
# Then run certbot
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot --webroot-path=/var/www/certbot \
    --email your@email.com --agree-tos --no-eff-email \
    -d api.htmlai.tech -d demo.htmlai.tech -d dashboard.htmlai.tech
```

### Start Services
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```
