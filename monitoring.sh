#!/bin/bash
# Monitoring script for OilGasFinder.com

echo "📊 OilGasFinder.com System Status"
echo "=================================="

# Check Docker services
echo -e "\n🐳 Docker Services:"
docker-compose -f docker-compose.prod.yml ps

# Check disk usage
echo -e "\n💾 Disk Usage:"
df -h

# Check memory usage
echo -e "\n🧠 Memory Usage:"
free -h

# Check Docker stats
echo -e "\n📈 Container Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# Check logs for errors
echo -e "\n🔍 Recent Errors in Logs:"
echo "Backend errors:"
docker-compose -f docker-compose.prod.yml logs backend 2>&1 | grep -i error | tail -5 || echo "No recent errors"

echo -e "\nFrontend errors:"
docker-compose -f docker-compose.prod.yml logs frontend 2>&1 | grep -i error | tail -5 || echo "No recent errors"

echo -e "\nNginx errors:"
docker-compose -f docker-compose.prod.yml logs nginx 2>&1 | grep -i error | tail -5 || echo "No recent errors"

# Test website accessibility
echo -e "\n🌐 Website Accessibility Test:"
if curl -f -s https://oilgasfinder.com > /dev/null; then
    echo "✅ Website is accessible"
else
    echo "❌ Website is not accessible"
fi

# Test API
echo -e "\n🔧 API Health Check:"
if curl -f -s https://oilgasfinder.com/api/status > /dev/null; then
    echo "✅ API is responding"
else
    echo "❌ API is not responding"
fi

# Check SSL certificate
echo -e "\n🔒 SSL Certificate Status:"
ssl_expiry=$(echo | openssl s_client -connect oilgasfinder.com:443 -servername oilgasfinder.com 2>/dev/null | openssl x509 -noout -dates | grep notAfter | cut -d= -f2)
if [ ! -z "$ssl_expiry" ]; then
    echo "✅ SSL Certificate expires: $ssl_expiry"
else
    echo "❌ SSL Certificate check failed"
fi

echo -e "\n📊 Monitoring completed at $(date)"
