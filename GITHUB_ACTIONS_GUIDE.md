# 🚀 GitHub Actions CI/CD Guide - China Car Parts

This guide explains the complete CI/CD pipeline configured for your repository.

## 📊 Workflow Overview

Your repository includes **7 GitHub Actions workflows**:

### 1. **CI Workflow** (`ci.yml`)
- **Trigger**: Push to `main`, `staging`, `develop` or PR
- **Purpose**: Continuous Integration testing
- **Features**:
  - Python 3.11+ testing
  - Node.js frontend building
  - Code quality checks (Black, isort, flake8, mypy)
  - Security scanning (Bandit, Safety)
  - Test coverage reporting
  - Artifact upload

### 2. **Staging Deployment** (`cd-staging.yml`)
- **Trigger**: Push to `staging` branch
- **Purpose**: Deploy to staging environment
- **Features**:
  - SSH deployment to staging server
  - Service restart and health checks
  - Smoke testing
  - Deployment notifications

### 3. **Production Deployment** (`cd-production.yml`)
- **Trigger**: Push to `main` branch
- **Purpose**: Deploy to production environment
- **Features**:
  - Blue-green deployment strategy
  - Zero-downtime deployments
  - Health checks and monitoring
  - Automatic rollback on failure

### 4. **Security Scanning** (`security.yml`)
- **Trigger**: Daily at 2 AM UTC, on demand
- **Purpose**: Comprehensive security analysis
- **Features**:
  - SAST scanning (Semgrep)
  - Dependency vulnerability scanning (Snyk)
  - Secret detection (GitLeaks)
  - Infrastructure scanning (Checkov)
  - Container scanning (Trivy)

### 5. **Performance Testing** (`performance.yml`)
- **Trigger**: Weekly, on demand
- **Purpose**: Performance and load testing
- **Features**:
  - API performance testing
  - Frontend performance (Lighthouse CI)
  - Load testing with Locust
  - Performance regression detection

### 6. **Dependencies Management** (`dependencies.yml`)
- **Trigger**: Weekly on Mondays
- **Purpose**: Keep dependencies updated
- **Features**:
  - Python dependency updates
  - Node.js dependency updates
  - Security patch application
  - Automated PR creation

### 7. **Branch Protection** (Configured in GitHub)
- **Purpose**: Ensure code quality
- **Features**:
  - Required status checks
  - Pull request reviews
  - Branch protection rules

## 🔧 Required GitHub Secrets

### **Core Application Secrets**
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ADMIN_IDS=123456789,987654321

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
```

### **Staging Environment**
```bash
STAGING_SSH_PRIVATE_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
STAGING_HOST=your-staging-server.com
STAGING_USER=partsbot
STAGING_API_URL=https://api-staging.yourdomain.com
STAGING_FRONTEND_ORIGIN=https://staging.yourdomain.com
```

### **Production Environment**
```bash
PROD_SSH_PRIVATE_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
PROD_HOST=your-production-server.com
PROD_USER=partsbot
PROD_API_URL=https://api.yourdomain.com
PROD_FRONTEND_ORIGIN=https://yourdomain.com
```

### **Optional Security Secrets**
```bash
SEMGREP_APP_TOKEN=your_semgrep_token
SNYK_TOKEN=your_snyk_token
GITLEAKS_LICENSE=your_gitleaks_license
LHCI_GITHUB_APP_TOKEN=your_lighthouse_token
```

## 🚀 Deployment Workflow

### Development Process
1. **Feature Development**:
   ```bash
   git checkout -b feature/new-feature
   # Make changes
   git commit -m "feat: add new feature"
   git push origin feature/new-feature
   # Create PR via GitHub
   ```

2. **Code Review**: PR triggers CI pipeline
3. **Merge to Staging**: Automatically deploys to staging
4. **Staging Testing**: Manual testing and validation
5. **Production Deployment**: Merge to main triggers production deployment

### Deployment Triggers
- **Staging**: Push to `staging` branch
- **Production**: Push to `main` branch
- **Security**: Daily automatic scans
- **Performance**: Weekly testing
- **Dependencies**: Weekly updates

## 📊 Monitoring & Notifications

### Deployment Status
- **Success**: Green checkmark in GitHub Actions
- **Failure**: Red X with detailed error logs
- **Notifications**: Slack/Discord webhooks (if configured)

### Health Checks
- **API Health**: `GET /health` endpoint
- **Service Status**: Systemd service monitoring
- **Database**: Connection and query performance
- **Frontend**: Lighthouse performance scores

## 🔒 Security Features

### Automated Security Scanning
- **Code Analysis**: Semgrep SAST scanning
- **Dependencies**: Snyk vulnerability scanning
- **Secrets**: GitLeaks secret detection
- **Infrastructure**: Checkov policy scanning
- **Containers**: Trivy container scanning

### Security Workflow
1. **Daily Scans**: Automatic security analysis
2. **PR Scans**: Security checks on every PR
3. **Alert System**: Immediate notifications for critical issues
4. **Compliance**: OWASP Top 10 and security best practices

## 📈 Performance Monitoring

### Performance Metrics
- **API Response Time**: < 200ms target
- **Frontend Load Time**: < 3s target
- **Database Queries**: < 100ms target
- **Uptime**: 99.9% target

### Performance Testing
- **Load Testing**: 1000+ concurrent users
- **Stress Testing**: System breaking points
- **Regression Testing**: Performance comparison
- **Monitoring**: Real-time performance metrics

## 🚨 Troubleshooting

### Common Issues

#### 1. **CI Pipeline Failures**
```bash
# Check logs in GitHub Actions
# Common fixes:
# - Update dependencies
# - Fix linting errors
# - Update test cases
```

#### 2. **Deployment Failures**
```bash
# Check deployment logs
# Verify server access
# Check service status
# Validate configuration
```

#### 3. **Security Scan Failures**
```bash
# Review security reports
# Fix vulnerabilities
# Update dependencies
# Configure secrets properly
```

### Rollback Procedures
- **Automatic**: Failed health checks trigger rollback
- **Manual**: Use deployment scripts for manual rollback
- **Database**: Alembic migration rollback support

## 📚 Workflow Files Location

All workflow files are located in `.github/workflows/`:

```
.github/workflows/
├── ci.yml                 # Continuous Integration
├── cd-staging.yml         # Staging Deployment
├── cd-production.yml      # Production Deployment
├── security.yml           # Security Scanning
├── performance.yml        # Performance Testing
├── dependencies.yml       # Dependency Updates
└── README.md              # Workflow Documentation
```

## 🔄 Maintenance

### Regular Tasks
- **Weekly**: Review security and performance reports
- **Monthly**: Update dependencies and review configurations
- **Quarterly**: Review and optimize CI/CD pipeline

### Monitoring
- **GitHub Actions**: Monitor workflow success rates
- **Deployment**: Track deployment frequency and success
- **Performance**: Monitor response times and uptime
- **Security**: Review security scan results

## 📞 Support

### Resources
- **GitHub Actions**: [Official Documentation](https://docs.github.com/en/actions)
- **Workflow Logs**: Available in repository Actions tab
- **Issues**: Create GitHub issues for problems
- **Discussions**: Use GitHub Discussions for questions

### Emergency Contacts
- **DevOps**: [Your DevOps Contact]
- **Development**: [Your Development Contact]
- **Security**: [Your Security Contact]

---

**Your CI/CD pipeline is production-ready and fully automated! 🎉**
