# html.ai Vultr Deployment Guide

## Quick Start (5 minutes)

### Step 1: Create Vultr VPS

1. Go to [Vultr.com](https://vultr.com) and log in
2. Click **Deploy New Server**
3. Choose:
   - **Type**: Cloud Compute (Shared CPU)
   - **Location**: Pick closest to your users (e.g., New York, Los Angeles)
   - **Image**: Ubuntu 22.04 LTS x64
   - **Plan**: $12/mo (1 vCPU, 2GB RAM, 55GB SSD) - sufficient for demo
     - Or $24/mo (2 vCPU, 4GB RAM) for better performance
   - **Additional Features**: Enable IPv4
   - **SSH Keys**: Add your SSH key (recommended) or use password
   - **Hostname**: `htmlai-server`
4. Click **Deploy Now**
5. Wait ~2 minutes for server to be ready
6. Copy the IP address

### Step 2: Configure DNS

Go to your domain registrar (where you bought htmlai.tech) and add these DNS records:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | YOUR_VULTR_IP | 300 |
| A | www | YOUR_VULTR_IP | 300 |
| A | api | YOUR_VULTR_IP | 300 |
| A | demo | YOUR_VULTR_IP | 300 |
| A | dashboard | YOUR_VULTR_IP | 300 |

Wait 5-10 minutes for DNS to propagate.

### Step 3: SSH into Server

```bash
ssh root@YOUR_VULTR_IP
```

### Step 4: Run Deployment Script

```bash
# Clone the repository
git clone https://github.com/tanujdargan/html.ai.git /opt/htmlai
cd /opt/htmlai/deploy

# Make script executable and run
chmod +x setup.sh
./setup.sh
```

### Step 5: Add Your OpenAI API Key

```bash
nano /opt/htmlai/deploy/.env
```

Add your key:
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
- **Website**: https://htmlai.tech
- **API**: https://api.htmlai.tech
- **Demo Store A**: https://demo.htmlai.tech/demo-business-a.html
- **Demo Store B**: https://demo.htmlai.tech/demo-business-b.html
- **Dashboard**: https://dashboard.htmlai.tech

---

## Manual Deployment (if script fails)

### 1. Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### 2. Clone Repository

```bash
git clone https://github.com/tanujdargan/html.ai.git /opt/htmlai
cd /opt/htmlai/deploy
```

### 3. Create Environment File

```bash
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-api-key-here
DOMAIN=htmlai.tech
EOF
```

### 4. Update URLs for Production

```bash
# Update all localhost references to production URLs
cd /opt/htmlai

# Demo business pages
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' htmlTag/demo-business-a.html
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' htmlTag/demo-business-b.html

# Dashboard
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' htmlTag/admin-dashboard.html
sed -i 's|http://localhost:3001|https://api.htmlai.tech/analytics|g' htmlTag/admin-dashboard.html

# SDK
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' htmlTag/sdk/src/AiOptimizeElement_v2.js
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' htmlTag/sdk/src/rewardbutton.js
```

### 5. Get SSL Certificates

```bash
cd /opt/htmlai/deploy

# Start nginx temporarily for certificate generation
docker-compose -f docker-compose.prod.yml up -d nginx

# Get certificates
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@htmlai.tech \
    --agree-tos \
    --no-eff-email \
    -d htmlai.tech \
    -d www.htmlai.tech \
    -d api.htmlai.tech \
    -d demo.htmlai.tech \
    -d dashboard.htmlai.tech
```

### 6. Start All Services

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## Useful Commands

### View Logs
```bash
cd /opt/htmlai/deploy

# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f engine
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Restart Services
```bash
cd /opt/htmlai/deploy

# All services
docker-compose -f docker-compose.prod.yml restart

# Specific service
docker-compose -f docker-compose.prod.yml restart engine
```

### Update Code
```bash
cd /opt/htmlai
git pull origin main
cd deploy
docker-compose -f docker-compose.prod.yml up -d --build
```

### Check Service Status
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Access MongoDB
```bash
docker exec -it htmlai-mongo mongosh
```

### Clear Database (if needed)
```bash
docker exec -it htmlai-mongo mongosh --eval "use html_ai; db.dropDatabase();"
```

---

## Troubleshooting

### SSL Certificate Issues
```bash
# Check certificate status
docker-compose -f docker-compose.prod.yml run --rm certbot certificates

# Force renewal
docker-compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal
docker-compose -f docker-compose.prod.yml restart nginx
```

### API Not Responding
```bash
# Check engine logs
docker-compose -f docker-compose.prod.yml logs engine

# Check if OpenAI key is set
docker exec htmlai-engine env | grep OPENAI
```

### MongoDB Connection Issues
```bash
# Check mongo status
docker-compose -f docker-compose.prod.yml logs mongo

# Restart mongo
docker-compose -f docker-compose.prod.yml restart mongo
```

---

## Cost Estimate

| Resource | Monthly Cost |
|----------|-------------|
| Vultr VPS (2GB) | $12 |
| Domain (yearly/12) | ~$1 |
| **Total** | **~$13/month** |

With your $250 Vultr credits, you can run this for **~19 months** on the basic plan!

---

## Architecture

```
                    ┌─────────────────┐
                    │   Cloudflare    │ (optional CDN)
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Vultr VPS      │
                    │  Ubuntu 22.04   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
    ┌─────────▼─────────┐    │    ┌─────────▼─────────┐
    │  Nginx (443/80)   │────┼────│  Let's Encrypt    │
    │  Reverse Proxy    │    │    │  SSL Certs        │
    └─────────┬─────────┘    │    └───────────────────┘
              │              │
    ┌─────────┴─────────────────────┬───────────────────┐
    │                               │                   │
┌───▼───┐  ┌───▼───┐  ┌───▼───┐  ┌───▼───┐  ┌───────▼───────┐
│Engine │  │Analyt.│  │Website│  │ Demo  │  │   Dashboard   │
│:3000  │  │:3001  │  │:4000  │  │static │  │    static     │
└───┬───┘  └───┬───┘  └───────┘  └───────┘  └───────────────┘
    │          │
    └────┬─────┘
         │
    ┌────▼────┐
    │ MongoDB │
    │ :27017  │
    └─────────┘
```
