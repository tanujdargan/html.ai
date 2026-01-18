#!/bin/bash

# ===========================================
# html.ai Backend Deployment Script
# Website is on Vercel (htmlai.tech)
# This deploys: api, demo, dashboard subdomains
# ===========================================

set -e

DOMAIN="htmlai.tech"
EMAIL="admin@htmlai.tech"  # Change to your email

echo "=========================================="
echo "html.ai Backend Deployment"
echo "=========================================="
echo "Website: htmlai.tech (Vercel)"
echo "API: api.htmlai.tech (this server)"
echo "Demo: demo.htmlai.tech (this server)"
echo "Dashboard: dashboard.htmlai.tech (this server)"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo ./setup.sh)"
    exit 1
fi

# ===========================================
# Step 1: System Updates
# ===========================================
echo ""
echo "[1/7] Updating system packages..."
apt update && apt upgrade -y

# ===========================================
# Step 2: Install Docker
# ===========================================
echo ""
echo "[2/7] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
else
    echo "Docker already installed"
fi

# ===========================================
# Step 3: Install Docker Compose
# ===========================================
echo ""
echo "[3/7] Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo "Docker Compose already installed"
fi

# ===========================================
# Step 4: Setup directories
# ===========================================
echo ""
echo "[4/7] Setting up directories..."
mkdir -p /opt/htmlai/deploy/certbot/conf
mkdir -p /opt/htmlai/deploy/certbot/www

cd /opt/htmlai

if [ -d ".git" ]; then
    echo "Updating existing repository..."
    git pull origin main
else
    echo "Cloning repository..."
    git clone https://github.com/tanujdargan/html.ai.git .
fi

# ===========================================
# Step 5: Create .env file
# ===========================================
echo ""
echo "[5/7] Setting up environment..."
if [ ! -f "/opt/htmlai/deploy/.env" ]; then
    cat > /opt/htmlai/deploy/.env << 'ENVFILE'
# OpenAI API Key (required for AI generation)
OPENAI_API_KEY=your_openai_api_key_here
ENVFILE
    echo ""
    echo "!!! IMPORTANT !!!"
    echo "Edit /opt/htmlai/deploy/.env and add your OPENAI_API_KEY"
    echo ""
fi

# ===========================================
# Step 6: Update URLs for production
# ===========================================
echo ""
echo "[6/7] Updating URLs for production..."

# Update demo-business-a.html
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' /opt/htmlai/htmlTag/demo-business-a.html
sed -i 's|href="demo-business-b.html"|href="/demo-business-b.html"|g' /opt/htmlai/htmlTag/demo-business-a.html

# Update demo-business-b.html
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' /opt/htmlai/htmlTag/demo-business-b.html
sed -i 's|href="demo-business-a.html"|href="/demo-business-a.html"|g' /opt/htmlai/htmlTag/demo-business-b.html

# Update admin-dashboard.html
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' /opt/htmlai/htmlTag/admin-dashboard.html
sed -i 's|http://localhost:3001|https://api.htmlai.tech/analytics|g' /opt/htmlai/htmlTag/admin-dashboard.html

# Update SDK files
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' /opt/htmlai/htmlTag/sdk/src/AiOptimizeElement_v2.js
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' /opt/htmlai/htmlTag/sdk/src/AiOptimizeElement.js
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' /opt/htmlai/htmlTag/sdk/src/rewardbutton.js

echo "URLs updated successfully"

# ===========================================
# Step 7: SSL Certificate & Start Services
# ===========================================
echo ""
echo "[7/7] Setting up SSL and starting services..."

cd /opt/htmlai/deploy

# Create temporary nginx config for certificate generation
cat > /opt/htmlai/deploy/nginx/conf.d/temp.conf << 'TMPCONF'
server {
    listen 80;
    server_name api.htmlai.tech demo.htmlai.tech dashboard.htmlai.tech;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'Setting up SSL...';
        add_header Content-Type text/plain;
    }
}
TMPCONF

# Remove the main config temporarily
mv /opt/htmlai/deploy/nginx/conf.d/htmlai.conf /opt/htmlai/deploy/nginx/conf.d/htmlai.conf.bak 2>/dev/null || true

# Start nginx for certificate generation
docker-compose -f docker-compose.prod.yml up -d nginx
sleep 5

# Get SSL certificates
echo "Requesting SSL certificates..."
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d api.$DOMAIN \
    -d demo.$DOMAIN \
    -d dashboard.$DOMAIN

# Restore main nginx config
rm /opt/htmlai/deploy/nginx/conf.d/temp.conf
mv /opt/htmlai/deploy/nginx/conf.d/htmlai.conf.bak /opt/htmlai/deploy/nginx/conf.d/htmlai.conf 2>/dev/null || git checkout /opt/htmlai/deploy/nginx/conf.d/htmlai.conf

# Start all services
echo "Starting all services..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Your services are now available at:"
echo "  - Website:   https://htmlai.tech (Vercel)"
echo "  - API:       https://api.htmlai.tech"
echo "  - Demo A:    https://demo.htmlai.tech/demo-business-a.html"
echo "  - Demo B:    https://demo.htmlai.tech/demo-business-b.html"
echo "  - Dashboard: https://dashboard.htmlai.tech"
echo ""
echo "IMPORTANT: Add your OpenAI API key:"
echo "  1. nano /opt/htmlai/deploy/.env"
echo "  2. Add: OPENAI_API_KEY=sk-your-key-here"
echo "  3. docker-compose -f /opt/htmlai/deploy/docker-compose.prod.yml restart engine"
echo ""
echo "View logs: docker-compose -f /opt/htmlai/deploy/docker-compose.prod.yml logs -f"
echo ""
