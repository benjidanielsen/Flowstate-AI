# Flowstate-AI Deployment Guide

## Prerequisites

- Ubuntu 22.04 LTS or later
- Python 3.11+
- Node.js 20+
- Redis Server
- SQLite3
- Git
- Nginx (for production)
- SSL Certificate (for HTTPS)

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here-use-os-urandom-24
FLASK_ENV=production
FLASK_DEBUG=0

# Admin Credentials
ADMIN_USERNAME=your-admin-username
ADMIN_PASSWORD_HASH=your-hashed-password

# OpenAI API
OPENAI_API_KEY=your-openai-api-key

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Database
DATABASE_PATH=godmode-state.db

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/benjidanielsen/Flowstate-AI.git
cd Flowstate-AI
```

### 2. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Install Node.js Dependencies

```bash
# Backend
cd backend && npm install && cd ..

# Frontend
cd frontend && npm install && cd ..

# Python Worker
cd python-worker && npm install && cd ..
```

### 4. Install Redis

```bash
sudo apt update
sudo apt install redis-server -y
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 5. Initialize Database

```bash
python3 -c "from unified_dashboard import init_db; init_db()"
```

### 6. Build Frontend

```bash
cd frontend
npm run build
cd ..
```

## Running the Application

### Development Mode

```bash
# Start Redis
sudo systemctl start redis-server

# Start Unified Dashboard
python3 unified_dashboard.py

# In separate terminals, start other services as needed
python3 backend/crm_api.py
python3 agents/crm_automation_agent.py
python3 brain/autonomous_task_system.py
python3 brain/system_monitor.py
```

### Production Mode with Systemd

Create systemd service files for each component:

#### 1. Unified Dashboard Service

Create `/etc/systemd/system/flowstate-dashboard.service`:

```ini
[Unit]
Description=Flowstate-AI Unified Dashboard
After=network.target redis-server.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Flowstate-AI
Environment="PATH=/usr/bin:/usr/local/bin"
EnvironmentFile=/home/ubuntu/Flowstate-AI/.env
ExecStart=/usr/bin/python3 unified_dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. CRM API Service

Create `/etc/systemd/system/flowstate-crm-api.service`:

```ini
[Unit]
Description=Flowstate-AI CRM API
After=network.target redis-server.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Flowstate-AI
Environment="PATH=/usr/bin:/usr/local/bin"
EnvironmentFile=/home/ubuntu/Flowstate-AI/.env
ExecStart=/usr/bin/python3 backend/crm_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. Autonomous Task System Service

Create `/etc/systemd/system/flowstate-task-system.service`:

```ini
[Unit]
Description=Flowstate-AI Autonomous Task System
After=network.target redis-server.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Flowstate-AI
Environment="PATH=/usr/bin:/usr/local/bin"
EnvironmentFile=/home/ubuntu/Flowstate-AI/.env
ExecStart=/usr/bin/python3 brain/autonomous_task_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 4. System Monitor Service

Create `/etc/systemd/system/flowstate-monitor.service`:

```ini
[Unit]
Description=Flowstate-AI System Monitor
After=network.target redis-server.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Flowstate-AI
Environment="PATH=/usr/bin:/usr/local/bin"
EnvironmentFile=/home/ubuntu/Flowstate-AI/.env
ExecStart=/usr/bin/python3 brain/system_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Enable and Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable flowstate-dashboard
sudo systemctl enable flowstate-crm-api
sudo systemctl enable flowstate-task-system
sudo systemctl enable flowstate-monitor

sudo systemctl start flowstate-dashboard
sudo systemctl start flowstate-crm-api
sudo systemctl start flowstate-task-system
sudo systemctl start flowstate-monitor
```

## Nginx Configuration

Create `/etc/nginx/sites-available/flowstate-ai`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Main Dashboard
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # CRM API
    location /api/crm {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static {
        alias /home/ubuntu/Flowstate-AI/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/flowstate-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL Certificate with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## Monitoring and Maintenance

### View Service Logs

```bash
# Dashboard logs
sudo journalctl -u flowstate-dashboard -f

# CRM API logs
sudo journalctl -u flowstate-crm-api -f

# Task System logs
sudo journalctl -u flowstate-task-system -f

# Monitor logs
sudo journalctl -u flowstate-monitor -f
```

### Check Service Status

```bash
sudo systemctl status flowstate-dashboard
sudo systemctl status flowstate-crm-api
sudo systemctl status flowstate-task-system
sudo systemctl status flowstate-monitor
```

### Restart Services

```bash
sudo systemctl restart flowstate-dashboard
sudo systemctl restart flowstate-crm-api
sudo systemctl restart flowstate-task-system
sudo systemctl restart flowstate-monitor
```

## Database Backup

Create a backup script at `/home/ubuntu/backup-flowstate.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup SQLite database
cp /home/ubuntu/Flowstate-AI/godmode-state.db $BACKUP_DIR/godmode-state-$DATE.db

# Backup Redis data
redis-cli SAVE
cp /var/lib/redis/dump.rdb $BACKUP_DIR/redis-$DATE.rdb

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +30 -delete

echo "Backup completed: $DATE"
```

Make it executable and add to cron:

```bash
chmod +x /home/ubuntu/backup-flowstate.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add line:
0 2 * * * /home/ubuntu/backup-flowstate.sh >> /home/ubuntu/backup.log 2>&1
```

## Security Checklist

- [ ] Change default admin credentials
- [ ] Set strong FLASK_SECRET_KEY
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure firewall (UFW)
- [ ] Set up fail2ban for brute-force protection
- [ ] Enable Redis authentication
- [ ] Restrict Redis to localhost only
- [ ] Set up regular database backups
- [ ] Enable system monitoring and alerting
- [ ] Review and update dependencies regularly
- [ ] Configure log rotation
- [ ] Set up intrusion detection (optional)

## Firewall Configuration

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

## Troubleshooting

### Dashboard won't start

```bash
# Check logs
sudo journalctl -u flowstate-dashboard -n 50

# Verify environment variables
cat /home/ubuntu/Flowstate-AI/.env

# Check Python dependencies
pip3 list
```

### Redis connection errors

```bash
# Check Redis status
sudo systemctl status redis-server

# Test Redis connection
redis-cli ping

# Check Redis logs
sudo journalctl -u redis-server -n 50
```

### High memory usage

```bash
# Check system resources
htop

# Check Redis memory
redis-cli INFO memory

# Clear Redis cache if needed
redis-cli FLUSHDB
```

## Performance Optimization

1. **Enable Redis persistence:**
   Edit `/etc/redis/redis.conf`:
   ```
   save 900 1
   save 300 10
   save 60 10000
   ```

2. **Optimize SQLite:**
   ```sql
   PRAGMA journal_mode=WAL;
   PRAGMA synchronous=NORMAL;
   PRAGMA cache_size=10000;
   ```

3. **Enable Nginx caching:**
   Add to nginx config:
   ```nginx
   proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;
   proxy_cache my_cache;
   ```

## Support

For issues and questions:
- GitHub Issues: https://github.com/benjidanielsen/Flowstate-AI/issues
- Documentation: https://github.com/benjidanielsen/Flowstate-AI/docs

---

**Last Updated:** October 7, 2025  
**Version:** 2.0
