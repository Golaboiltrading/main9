#!/bin/bash
# OilGasFinder.com Production Deployment Script

set -e

echo "🚀 Starting OilGasFinder.com deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p nginx/logs
mkdir -p nginx/ssl
mkdir -p backend/logs
sudo mkdir -p /etc/letsencrypt
sudo mkdir -p /var/www/certbot

# Copy environment file
if [ ! -f .env ]; then
    print_status "Creating production environment file..."
    cp .env.production .env
    print_warning "Please edit .env file with your actual credentials before proceeding!"
    print_warning "Required: MONGO_ROOT_PASSWORD, SECRET_KEY, PAYPAL credentials"
    read -p "Press Enter after you've updated the .env file..."
fi

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || true

# Remove old containers and images (optional cleanup)
read -p "Do you want to remove old Docker images to save space? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Cleaning up old Docker images..."
    docker system prune -f
fi

# Build and start services
print_status "Building and starting all services..."
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for services to start
print_status "Waiting for services to start..."
sleep 30

# Check if services are running
print_status "Checking service status..."
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    print_status "✅ Services are running successfully!"
else
    print_error "❌ Some services failed to start. Check logs with: docker-compose -f docker-compose.prod.yml logs"
    exit 1
fi

# Test backend health
print_status "Testing backend health..."
if curl -f http://localhost:8001/api/status &>/dev/null; then
    print_status "✅ Backend is responding"
else
    print_warning "⚠️  Backend health check failed. Check logs: docker-compose -f docker-compose.prod.yml logs backend"
fi

# Test frontend
print_status "Testing frontend..."
if curl -f http://localhost:3000 &>/dev/null; then
    print_status "✅ Frontend is responding"
else
    print_warning "⚠️  Frontend health check failed. Check logs: docker-compose -f docker-compose.prod.yml logs frontend"
fi

# Check MongoDB
print_status "Testing MongoDB connection..."
if docker exec oilgasfinder-mongo mongosh --eval "db.runCommand({ping: 1})" &>/dev/null; then
    print_status "✅ MongoDB is running"
else
    print_warning "⚠️  MongoDB connection failed. Check logs: docker-compose -f docker-compose.prod.yml logs mongo"
fi

# SSL Certificate setup
print_status "Setting up SSL certificate..."
print_warning "Make sure your domain DNS is pointing to this server before running SSL setup!"
read -p "Is your DNS properly configured and pointing to this server? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Generating SSL certificate..."
    
    # Update email in certbot command
    read -p "Enter your email for SSL certificate: " ssl_email
    
    # Stop nginx temporarily
    docker-compose -f docker-compose.prod.yml stop nginx
    
    # Run certbot
    docker run --rm \
        -v /etc/letsencrypt:/etc/letsencrypt \
        -v /var/www/certbot:/var/www/certbot \
        -p 80:80 \
        certbot/certbot certonly \
        --standalone \
        --email $ssl_email \
        --agree-tos \
        --no-eff-email \
        -d oilgasfinder.com \
        -d www.oilgasfinder.com
    
    # Restart nginx with SSL
    docker-compose -f docker-compose.prod.yml start nginx
    
    # Test HTTPS
    if curl -f https://oilgasfinder.com &>/dev/null; then
        print_status "✅ HTTPS is working!"
    else
        print_warning "⚠️  HTTPS setup may have issues. Check nginx logs."
    fi
else
    print_warning "Skipping SSL setup. You can run it later when DNS is ready."
fi

# Final status check
print_status "Final deployment status check..."
echo
echo "=== SERVICE STATUS ==="
docker-compose -f docker-compose.prod.yml ps
echo
echo "=== USEFUL COMMANDS ==="
echo "View logs: docker-compose -f docker-compose.prod.yml logs [service_name]"
echo "Restart: docker-compose -f docker-compose.prod.yml restart [service_name]"
echo "Stop all: docker-compose -f docker-compose.prod.yml down"
echo "Update: docker-compose -f docker-compose.prod.yml up --build -d"
echo
echo "=== ACCESS URLS ==="
echo "🌐 Website: https://oilgasfinder.com"
echo "🔧 API: https://oilgasfinder.com/api"
echo "📊 Sitemap: https://oilgasfinder.com/sitemap.xml"
echo "🤖 Robots: https://oilgasfinder.com/robots.txt"
echo

print_status "🎉 Deployment completed! Your Oil & Gas trading platform is now live!"
print_status "🔍 Next steps:"
echo "1. Test all functionality on https://oilgasfinder.com"
echo "2. Submit sitemap to Google Search Console"
echo "3. Setup Google Analytics and Hotjar tracking"
echo "4. Monitor logs and performance"
echo "5. Start your marketing campaigns!"
