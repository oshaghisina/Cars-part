# 🚨 Deployment Troubleshooting Guide

This guide helps diagnose and resolve common deployment issues for the China Car Parts application.

## 📋 Quick Diagnostic Checklist

### Pre-Deployment Issues
- [ ] SSH connection to server works
- [ ] Sufficient disk space (>1GB free)
- [ ] Required commands available (git, python3.11, pip, npm, systemctl, nginx)
- [ ] Target ports are available
- [ ] Repository access is working
- [ ] Database is accessible

### Post-Deployment Issues
- [ ] Services are running (`systemctl status`)
- [ ] Health endpoints respond (`curl /api/v1/health`)
- [ ] Nginx is serving requests
- [ ] Database migrations completed
- [ ] Frontend assets are built and served

## 🔍 Common Issues and Solutions

### 1. SSH Connection Issues

#### Problem: Cannot connect to deployment server
```bash
ssh: connect to host <server> port 22: Connection refused
```

**Solutions:**
1. Verify server is running and accessible:
   ```bash
   ping <server-ip>
   telnet <server-ip> 22
   ```

2. Check SSH key permissions:
   ```bash
   chmod 600 ~/.ssh/china_car_parts_key
   chmod 644 ~/.ssh/china_car_parts_key.pub
   ```

3. Test SSH connection:
   ```bash
   ssh -v -i ~/.ssh/china_car_parts_key root@<server-ip>
   ```

4. Check SSH configuration on server:
   ```bash
   sudo systemctl status ssh
   sudo journalctl -u ssh
   ```

### 2. Port Availability Issues

#### Problem: Port already in use
```bash
Port 8001 is already in use. Cannot deploy to environment.
```

**Solutions:**
1. Check what's using the port:
   ```bash
   sudo netstat -tulpn | grep :8001
   sudo lsof -i :8001
   ```

2. Stop conflicting services:
   ```bash
   sudo systemctl stop china-car-parts-api-blue
   sudo systemctl stop china-car-parts-api-green
   ```

3. Kill processes if necessary:
   ```bash
   sudo fuser -k 8001/tcp
   ```

### 3. Git Repository Issues

#### Problem: Failed to fetch from origin
```bash
Failed to fetch from origin repository
```

**Solutions:**
1. Check repository URL and access:
   ```bash
   git remote -v
   git ls-remote origin
   ```

2. Verify SSH key has repository access:
   ```bash
   ssh -T git@github.com
   ```

3. Check network connectivity:
   ```bash
   curl -I https://github.com
   ```

4. Update repository URL if needed:
   ```bash
   git remote set-url origin https://github.com/your-org/china-car-parts.git
   ```

### 4. Python Environment Issues

#### Problem: Python virtual environment not found
```bash
Python virtual environment not found at /opt/china-car-parts/venv
```

**Solutions:**
1. Create virtual environment:
   ```bash
   cd /opt/china-car-parts
   python3.11 -m venv venv
   ```

2. Verify Python version:
   ```bash
   python3.11 --version
   which python3.11
   ```

3. Install Python if missing:
   ```bash
   sudo apt update
   sudo apt install python3.11 python3.11-venv python3.11-dev
   ```

#### Problem: Failed to install Python dependencies
```bash
Failed to install Python dependencies after 3 attempts
```

**Solutions:**
1. Update pip:
   ```bash
   source venv/bin/activate
   pip install --upgrade pip
   ```

2. Clear pip cache:
   ```bash
   pip cache purge
   ```

3. Install dependencies individually:
   ```bash
   pip install -r requirements.txt --no-cache-dir
   ```

4. Check for conflicting packages:
   ```bash
   pip list
   pip check
   ```

### 5. Database Migration Issues

#### Problem: Database migration failed
```bash
Database migration failed. Check database connection and migration files.
```

**Solutions:**
1. Check database file permissions:
   ```bash
   ls -la /opt/china-car-parts/data/
   chmod 644 /opt/china-car-parts/data/china_car_parts.db
   ```

2. Verify Alembic configuration:
   ```bash
   alembic current
   alembic history
   ```

3. Check for migration conflicts:
   ```bash
   alembic heads
   alembic merge heads
   ```

4. Restore from backup if needed:
   ```bash
   cp /opt/backups/china-car-parts/staging_db_backup_*.db /opt/china-car-parts/data/china_car_parts.db
   ```

### 6. Frontend Build Issues

#### Problem: Frontend build failed
```bash
Frontend build failed. Check for build errors.
```

**Solutions:**
1. Check Node.js version:
   ```bash
   node --version
   npm --version
   ```

2. Clear npm cache:
   ```bash
   npm cache clean --force
   ```

3. Delete node_modules and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

4. Check for build errors:
   ```bash
   npm run build 2>&1 | tee build.log
   ```

### 7. Service Startup Issues

#### Problem: API service failed to start
```bash
Failed to start API service. Check logs with: journalctl -u china-car-parts-api-staging
```

**Solutions:**
1. Check service logs:
   ```bash
   sudo journalctl -u china-car-parts-api-staging -f
   sudo journalctl -u china-car-parts-api-staging --since "5 minutes ago"
   ```

2. Check service configuration:
   ```bash
   sudo systemctl cat china-car-parts-api-staging
   ```

3. Test service manually:
   ```bash
   cd /opt/china-car-parts
   source venv/bin/activate
   uvicorn app.api.main:app --host 0.0.0.0 --port 8001
   ```

4. Check for port conflicts:
   ```bash
   sudo netstat -tulpn | grep :8001
   ```

### 8. Health Check Issues

#### Problem: Health check failed
```bash
Health check failed for http://localhost:8001/api/v1/health after 30 attempts
```

**Solutions:**
1. Check if service is running:
   ```bash
   sudo systemctl status china-car-parts-api-staging
   ```

2. Test health endpoint manually:
   ```bash
   curl -v http://localhost:8001/api/v1/health
   curl -v http://localhost:8001/health
   ```

3. Check application logs:
   ```bash
   tail -f /opt/china-car-parts/logs/app.log
   ```

4. Verify database connectivity:
   ```bash
   cd /opt/china-car-parts
   source venv/bin/activate
   python -c "from app.db.database import engine; print('DB OK')"
   ```

### 9. Nginx Issues

#### Problem: Nginx reload failed
```bash
Failed to reload Nginx. Check configuration with: nginx -t
```

**Solutions:**
1. Test Nginx configuration:
   ```bash
   sudo nginx -t
   ```

2. Check Nginx error logs:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

3. Check configuration syntax:
   ```bash
   sudo nginx -T
   ```

4. Restart Nginx if needed:
   ```bash
   sudo systemctl restart nginx
   ```

### 10. Performance Issues

#### Problem: Slow deployment or high resource usage

**Solutions:**
1. Check system resources:
   ```bash
   htop
   df -h
   free -h
   ```

2. Monitor during deployment:
   ```bash
   watch -n 1 'ps aux | grep -E "(python|node|nginx)"'
   ```

3. Optimize build process:
   ```bash
   # Use npm ci instead of npm install
   # Enable parallel builds where possible
   # Use build cache
   ```

## 🛠️ Diagnostic Commands

### System Information
```bash
# Check system resources
htop
df -h
free -h
lscpu

# Check running services
systemctl list-units --state=running | grep china-car-parts

# Check network connections
netstat -tulpn | grep -E "(8001|8002|80|443)"
```

### Application Logs
```bash
# API service logs
sudo journalctl -u china-car-parts-api-staging -f

# Bot service logs
sudo journalctl -u china-car-parts-bot-staging -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Application logs
tail -f /opt/china-car-parts/logs/app.log
```

### Database Diagnostics
```bash
# Check database file
ls -la /opt/china-car-parts/data/china_car_parts.db

# Test database connection
cd /opt/china-car-parts
source venv/bin/activate
python -c "from app.db.database import engine; print(engine.execute('SELECT 1').fetchone())"

# Check migration status
alembic current
alembic history
```

### Network Diagnostics
```bash
# Test connectivity
curl -v http://localhost:8001/api/v1/health
curl -v https://yourdomain.com/api/v1/health

# Check DNS resolution
nslookup yourdomain.com
dig yourdomain.com

# Test SSL certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

## 📞 Emergency Procedures

### Rollback Deployment
```bash
# Quick rollback using blue-green deployment
./deployment/scripts/blue-green-deploy.sh --rollback

# Manual rollback
sudo systemctl stop china-car-parts-api-staging
sudo systemctl stop china-car-parts-bot-staging
# Restore previous version and restart services
```

### Emergency Service Restart
```bash
# Restart all services
sudo systemctl restart china-car-parts-api-staging
sudo systemctl restart china-car-parts-bot-staging
sudo systemctl restart nginx

# Check service status
sudo systemctl status china-car-parts-api-staging
sudo systemctl status china-car-parts-bot-staging
sudo systemctl status nginx
```

### Database Emergency
```bash
# Stop application services
sudo systemctl stop china-car-parts-api-staging
sudo systemctl stop china-car-parts-bot-staging

# Restore database from backup
cp /opt/backups/china-car-parts/staging_db_backup_*.db /opt/china-car-parts/data/china_car_parts.db

# Restart services
sudo systemctl start china-car-parts-api-staging
sudo systemctl start china-car-parts-bot-staging
```

## 📚 Additional Resources

- [Deployment Scripts Documentation](./DEPLOYMENT_SCRIPTS.md)
- [Configuration Guide](./CONFIGURATION_GUIDE.md)
- [Monitoring and Alerting](./MONITORING_GUIDE.md)
- [GitHub Actions Workflows](../.github/workflows/README.md)
- [Server Setup Guide](../SERVER_SETUP_GUIDE.md)

## 🆘 Getting Help

If you encounter issues not covered in this guide:

1. Check the deployment logs: `/opt/china-car-parts/logs/deployment.log`
2. Review system logs: `journalctl -u china-car-parts-*`
3. Check GitHub Actions logs for CI/CD issues
4. Contact the development team with:
   - Error messages
   - Deployment logs
   - System information
   - Steps to reproduce the issue
