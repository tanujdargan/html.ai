#!/bin/bash

# ===========================================
# html.ai Production Deployment Script
# For Vultr VPS with Ubuntu 22.04
# ===========================================

set -e

DOMAIN="htmlai.tech"
EMAIL="admin@htmlai.tech"  # Change this to your email

echo "=========================================="
echo "html.ai Production Deployment"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo ./setup.sh)"
    exit 1
fi

# ===========================================
# Step 1: System Updates
# ===========================================
echo "[1/8] Updating system packages..."
apt update && apt upgrade -y

# ===========================================
# Step 2: Install Docker
# ===========================================
echo "[2/8] Installing Docker..."
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
echo "[3/8] Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo "Docker Compose already installed"
fi

# ===========================================
# Step 4: Create directories
# ===========================================
echo "[4/8] Creating directories..."
mkdir -p /opt/htmlai
mkdir -p /opt/htmlai/deploy/certbot/conf
mkdir -p /opt/htmlai/deploy/certbot/www

# ===========================================
# Step 5: Clone/Update repository
# ===========================================
echo "[5/8] Setting up repository..."
cd /opt/htmlai

if [ -d ".git" ]; then
    echo "Updating existing repository..."
    git pull origin main
else
    echo "Cloning repository..."
    git clone https://github.com/tanujdargan/html.ai.git .
fi

# ===========================================
# Step 6: Create .env file
# ===========================================
echo "[6/8] Setting up environment..."
if [ ! -f "/opt/htmlai/deploy/.env" ]; then
    echo "Creating .env file..."
    cat > /opt/htmlai/deploy/.env << 'ENVFILE'
# OpenAI API Key (required for AI generation)
OPENAI_API_KEY=your_openai_api_key_here

# Domain configuration
DOMAIN=htmlai.tech
ENVFILE
    echo ""
    echo "!!! IMPORTANT !!!"
    echo "Edit /opt/htmlai/deploy/.env and add your OPENAI_API_KEY"
    echo ""
fi

# ===========================================
# Step 7: Initial SSL Setup (HTTP only first)
# ===========================================
echo "[7/8] Setting up initial nginx for SSL..."

# Create temporary nginx config for SSL certificate generation
cat > /opt/htmlai/deploy/nginx/conf.d/htmlai.conf << 'TMPCONF'
server {
    listen 80;
    server_name htmlai.tech www.htmlai.tech api.htmlai.tech demo.htmlai.tech dashboard.htmlai.tech;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'html.ai is setting up SSL...';
        add_header Content-Type text/plain;
    }
}
TMPCONF

# Start nginx for certificate generation
cd /opt/htmlai/deploy
docker-compose -f docker-compose.prod.yml up -d nginx

# Wait for nginx to start
sleep 5

# ===========================================
# Step 8: Generate SSL Certificate
# ===========================================
echo "[8/8] Generating SSL certificate..."
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN \
    -d api.$DOMAIN \
    -d demo.$DOMAIN \
    -d dashboard.$DOMAIN

# Restore full nginx config
git checkout deploy/nginx/conf.d/htmlai.conf

# ===========================================
# Update URLs in HTML files for production
# ===========================================
echo "Updating URLs for production..."

# Update demo-business-a.html
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' /opt/htmlai/htmlTag/demo-business-a.html
sed -i 's|href="demo-business-b.html"|href="https://demo.htmlai.tech/demo-business-b.html"|g' /opt/htmlai/htmlTag/demo-business-a.html

# Update demo-business-b.html
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' /opt/htmlai/htmlTag/demo-business-b.html
sed -i 's|href="demo-business-a.html"|href="https://demo.htmlai.tech/demo-business-a.html"|g' /opt/htmlai/htmlTag/demo-business-b.html

# Update admin-dashboard.html
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' /opt/htmlai/htmlTag/admin-dashboard.html
sed -i 's|http://localhost:3001|https://api.htmlai.tech/analytics|g' /opt/htmlai/htmlTag/admin-dashboard.html

# Update SDK
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' /opt/htmlai/htmlTag/sdk/src/AiOptimizeElement_v2.js
sed -i 's|http://localhost:3000|https://api.htmlai.tech|g' /opt/htmlai/htmlTag/sdk/src/rewardbutton.js

# ===========================================
# Start all services
# ===========================================
echo "Starting all services..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Your services are now available at:"
echo "  - Website:   https://htmlai.tech"
echo "  - API:       https://api.htmlai.tech"
echo "  - Demo:      https://demo.htmlai.tech"
echo "  - Dashboard: https://dashboard.htmlai.tech"
echo ""
echo "Next steps:"
echo "1. Edit /opt/htmlai/deploy/.env and add your OPENAI_API_KEY"
echo "2. Run: cd /opt/htmlai/deploy && docker-compose -f docker-compose.prod.yml restart engine"
echo ""
echo "To view logs:"
echo "  docker-compose -f /opt/htmlai/deploy/docker-compose.prod.yml logs -f"
echo ""
