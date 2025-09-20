# 🚀 Deployment Guide - China Car Parts

This guide covers the complete deployment process for the China Car Parts system to your GitHub repository.

## 📋 Prerequisites

### 1. GitHub Repository Setup
- Repository: `https://github.com/oshaghisina/Cars-part.git`
- Branch Protection: Configured for `main` and `staging` branches
- Required Status Checks: CI, Security, Performance

### 2. Required GitHub Secrets

Configure the following secrets in your GitHub repository settings:

#### **Core Secrets**
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/dbname
REDIS_URL=redis://host:port

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ADMIN_IDS=123456789,987654321

# JWT & Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
```

#### **Staging Environment**
```bash
STAGING_SSH_PRIVATE_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
STAGING_HOST=your-staging-server.com
STAGING_USER=partsbot
STAGING_API_URL=https://api-staging.yourdomain.com
STAGING_FRONTEND_ORIGIN=https://staging.yourdomain.com
```

#### **Production Environment**
```bash
PROD_SSH_PRIVATE_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
PROD_HOST=your-production-server.com
PROD_USER=partsbot
PROD_API_URL=https://api.yourdomain.com
PROD_FRONTEND_ORIGIN=https://yourdomain.com
```

#### **Optional Secrets (for enhanced features)**
```bash
# Security Scanning
SEMGREP_APP_TOKEN=your_semgrep_token
SNYK_TOKEN=your_snyk_token
GITLEAKS_LICENSE=your_gitleaks_license

# Performance Testing
LHCI_GITHUB_APP_TOKEN=your_lighthouse_token

# Notifications
SLACK_WEBHOOK_URL=your_slack_webhook
DISCORD_WEBHOOK_URL=your_discord_webhook
```

## 🔧 Initial Setup

### 1. Clone and Configure Repository

```bash
# Clone the repository
git clone https://github.com/oshaghisina/Cars-part.git
cd Cars-part

# Set up Git configuration
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add all files and make initial commit
git add .
git commit -m "Initial commit: China Car Parts system"
git push -u origin main
```

### 2. Configure Branch Protection

In GitHub repository settings:

1. Go to **Settings** → **Branches**
2. Add rule for `main` branch:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Restrict pushes that create files larger than 100MB
   - Status checks required: `CI`, `Security`, `Performance`

3. Add rule for `staging` branch:
   - ✅ Require status checks to pass before merging
   - Status checks required: `CI`, `Security`

### 3. Set Up Environments

In GitHub repository settings:

1. Go to **Settings** → **Environments**
2. Create `staging` environment:
   - Protection rules: Required reviewers (optional)
   - Environment secrets: Add all staging secrets
3. Create `production` environment:
   - Protection rules: Required reviewers (recommended)
   - Environment secrets: Add all production secrets

## 🚀 Deployment Process

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and test locally
# ... your development work ...

# 3. Commit changes
git add .
git commit -m "feat: add new feature"

# 4. Push and create PR
git push origin feature/new-feature
# Create PR via GitHub web interface
```

### Staging Deployment

```bash
# 1. Merge to staging branch
git checkout staging
git merge feature/new-feature
git push origin staging

# 2. GitHub Actions will automatically:
#    - Run CI pipeline
#    - Deploy to staging server
#    - Run smoke tests
#    - Notify deployment status
```

### Production Deployment

```bash
# 1. Merge to main branch (after staging approval)
git checkout main
git merge staging
git push origin main

# 2. GitHub Actions will automatically:
#    - Run full CI/CD pipeline
#    - Execute blue-green deployment
#    - Perform health checks
#    - Monitor deployment success
```

## 🔍 CI/CD Pipeline Overview

### Continuous Integration (CI)
- **Trigger**: Push to `main`, `staging`, `develop` or PR
- **Steps**:
  1. Code checkout
  2. Python environment setup
  3. Node.js environment setup
  4. Install dependencies
  5. Run linting (Black, isort, flake8, mypy)
  6. Run security scanning (Bandit, Safety)
  7. Run tests (unit, integration, E2E)
  8. Build frontend
  9. Generate coverage report
  10. Upload artifacts

### Continuous Deployment (CD)

#### Staging Deployment
- **Trigger**: Push to `staging` branch
- **Steps**:
  1. Run CI pipeline
  2. SSH to staging server
  3. Pull latest code
  4. Install dependencies
  5. Run database migrations
  6. Restart services
  7. Run smoke tests
  8. Notify deployment status

#### Production Deployment
- **Trigger**: Push to `main` branch
- **Steps**:
  1. Run CI pipeline
  2. SSH to production server
  3. Execute blue-green deployment
  4. Run health checks
  5. Switch traffic to new deployment
  6. Monitor deployment success
  7. Rollback on failure (automatic)

## 📊 Monitoring & Health Checks

### Health Check Endpoints
- **API Health**: `GET /health`
- **Database**: Automatic connection checks
- **Services**: Systemd service status monitoring
- **Performance**: Response time and throughput metrics

### Monitoring Dashboard
- **Staging**: `https://staging.yourdomain.com/admin`
- **Production**: `https://yourdomain.com/admin`
- **Analytics**: Real-time business metrics
- **Performance**: System performance indicators

## 🔒 Security Considerations

### Secrets Management
- All sensitive data stored in GitHub Secrets
- Environment-specific secret separation
- Automatic secret rotation (recommended)

### Security Scanning
- **SAST**: Semgrep for static analysis
- **Dependency**: Snyk for vulnerability scanning
- **Secrets**: GitLeaks for secret detection
- **Infrastructure**: Checkov for IaC scanning

### Access Control
- SSH key-based server access
- Environment-specific permissions
- Audit logging for all deployments

## 🚨 Troubleshooting

### Common Issues

#### 1. Deployment Failures
```bash
# Check deployment logs
ssh user@server "journalctl -u china-car-parts-api -f"

# Check service status
ssh user@server "systemctl status china-car-parts-api"
```

#### 2. Database Migration Issues
```bash
# Check migration status
ssh user@server "cd /opt/parts-bot && alembic current"

# Rollback migration
ssh user@server "cd /opt/parts-bot && alembic downgrade -1"
```

#### 3. Frontend Build Issues
```bash
# Check build logs in GitHub Actions
# Common issues: Node.js version, dependency conflicts
```

### Rollback Procedures

#### Automatic Rollback
- Triggered by failed health checks
- Reverts to previous working deployment
- Notifications sent to team

#### Manual Rollback
```bash
# 1. SSH to production server
ssh partsbot@yourdomain.com

# 2. Switch to previous deployment
sudo /opt/parts-bot/deployment/scripts/blue-green-deploy.sh rollback

# 3. Verify rollback success
curl https://api.yourdomain.com/health
```

## 📈 Performance Optimization

### Caching Strategy
- **Redis**: Session and API response caching
- **CDN**: Static asset delivery
- **Database**: Query optimization and indexing

### Scaling Considerations
- **Horizontal**: Multiple API instances
- **Vertical**: Server resource scaling
- **Database**: Read replicas for analytics

## 🔄 Maintenance

### Regular Tasks
- **Weekly**: Security updates and dependency updates
- **Monthly**: Performance review and optimization
- **Quarterly**: Infrastructure review and scaling assessment

### Backup Strategy
- **Database**: Daily automated backups
- **Code**: Git repository (automatic)
- **Configuration**: Environment-specific backups

## 📞 Support

### Emergency Contacts
- **DevOps**: [Your DevOps Contact]
- **Development**: [Your Development Contact]
- **Infrastructure**: [Your Infrastructure Contact]

### Escalation Process
1. Check deployment logs
2. Verify service status
3. Check monitoring dashboards
4. Execute rollback if necessary
5. Contact team leads for critical issues

---

**For additional support, refer to the main [README.md](README.md) or create an issue in the repository.**