# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the China Car Parts CI/CD pipeline.

## Linting Warnings

The linter may show warnings about "Context access might be invalid" for secrets. These are **false positives** and can be safely ignored because:

1. **GitHub Secrets are Available at Runtime**: The `secrets` context is provided by GitHub Actions at workflow execution time
2. **Proper Syntax**: All secret references use the correct `${{ secrets.SECRET_NAME }}` syntax
3. **Environment Protection**: Secrets are only accessible in protected environments
4. **Runtime Validation**: GitHub Actions validates secret access at runtime, not at lint time

### Common False Positive Warnings:
- `Context access might be invalid: STAGING_SSH_PRIVATE_KEY`
- `Context access might be invalid: PROD_API_URL`
- `Context access might be invalid: SNYK_TOKEN`
- And similar warnings for other secrets

### Why These Are Safe to Ignore:
- These secrets are properly configured in GitHub repository settings
- The workflows include proper error handling for missing secrets
- All secret references follow GitHub Actions best practices
- The linter cannot validate runtime secret availability

## Workflow Files

### CI Pipeline (`ci.yml`)
- **Purpose**: Continuous Integration with testing and quality gates
- **Triggers**: Push to any branch, Pull Requests to main/staging
- **Features**: Backend tests, Frontend tests, Security scanning, Code quality

### Security Scanning (`security.yml`)
- **Purpose**: Comprehensive security vulnerability scanning
- **Triggers**: Push to main/staging, Pull Requests, Weekly schedule
- **Features**: Python security (Bandit, Safety), Frontend security (npm audit, Snyk), Infrastructure scanning (Trivy, Checkov), Secret scanning (TruffleHog, GitLeaks)

### Performance Testing (`performance.yml`)
- **Purpose**: Performance and load testing
- **Triggers**: Push to main/staging, Manual dispatch
- **Features**: API load testing (Locust), Database performance (pytest-benchmark), Frontend performance (Lighthouse CI)

### Staging Deployment (`cd-staging.yml`)
- **Purpose**: Automated deployment to staging environment
- **Triggers**: Push to staging branch
- **Features**: Blue-green deployment, Health checks, Rollback capabilities

### Production Deployment (`cd-production.yml`)
- **Purpose**: Production deployment with blue-green strategy
- **Triggers**: Push to main branch, Manual dispatch
- **Features**: Zero-downtime deployment, Advanced monitoring, Automated rollback

### Dependencies (`dependencies.yml`)
- **Purpose**: Automated dependency updates
- **Triggers**: Weekly schedule, Manual dispatch
- **Features**: Python dependency updates, Node.js dependency updates, Automated PR creation

## Required Secrets

### Global Secrets (Available to all environments)
- `GITHUB_TOKEN` - Automatically provided by GitHub

### Staging Environment Secrets
- `STAGING_SSH_PRIVATE_KEY` - SSH private key for staging server access
- `STAGING_USER` - SSH username for staging server
- `STAGING_HOST` - Staging server hostname/IP
- `STAGING_API_URL` - Staging API URL for health checks
- `STAGING_FRONTEND_ORIGIN` - Staging frontend URL
- `STAGING_TELEGRAM_BOT_TOKEN` - Telegram bot token for staging
- `STAGING_ADMIN_TELEGRAM_IDS` - Admin Telegram IDs for staging
- `STAGING_SECRET_KEY` - Secret key for staging environment
- `STAGING_DATABASE_URL` - Database connection string for staging

### Production Environment Secrets
- `PROD_SSH_PRIVATE_KEY` - SSH private key for production server access
- `PROD_USER` - SSH username for production server
- `PROD_HOST` - Production server hostname/IP
- `PROD_API_URL` - Production API URL for health checks
- `PROD_FRONTEND_ORIGIN` - Production frontend URL
- `PROD_TELEGRAM_BOT_TOKEN` - Telegram bot token for production
- `PROD_ADMIN_TELEGRAM_IDS` - Admin Telegram IDs for production
- `PROD_SECRET_KEY` - Secret key for production environment
- `PROD_DATABASE_URL` - Database connection string for production

### Optional Security Tool Secrets
- `SEMGREP_APP_TOKEN` - Semgrep security scanning token
- `SNYK_TOKEN` - Snyk security scanning token
- `GITLEAKS_LICENSE` - GitLeaks license for secret scanning
- `LHCI_GITHUB_APP_TOKEN` - Lighthouse CI GitHub App token

## Environment Setup

### Staging Environment
1. Set up staging server with proper SSH access
2. Configure staging environment secrets in GitHub
3. Ensure staging server has required software (Python 3.11, Node.js 18, PostgreSQL, Nginx)

### Production Environment
1. Set up production server with proper SSH access
2. Configure production environment secrets in GitHub
3. Ensure production server has required software and security hardening
4. Set up SSL certificates and domain configuration

## Troubleshooting

### Common Issues

#### Workflow Fails with "Secret Not Found"
- **Cause**: Secret not configured in GitHub repository settings
- **Solution**: Add the missing secret to the appropriate environment

#### SSH Connection Fails
- **Cause**: Incorrect SSH private key or server configuration
- **Solution**: Verify SSH key format and server access

#### Health Checks Fail
- **Cause**: Application not starting properly or incorrect URLs
- **Solution**: Check application logs and verify configuration

#### Deployment Timeout
- **Cause**: Server performance issues or network problems
- **Solution**: Check server resources and network connectivity

### Debugging Tips

1. **Check Workflow Logs**: Review the detailed logs in GitHub Actions
2. **Verify Secrets**: Ensure all required secrets are configured
3. **Test Manually**: Run deployment scripts manually on the server
4. **Check Server Logs**: Review application and system logs on the target server
5. **Validate Configuration**: Ensure all configuration files are correct

## Best Practices

1. **Secret Management**: Use GitHub's environment protection for sensitive secrets
2. **Branch Protection**: Enable branch protection rules for main and staging branches
3. **Review Process**: Require pull request reviews for production deployments
4. **Monitoring**: Set up alerts for deployment failures and application issues
5. **Backup Strategy**: Implement automated backups before deployments
6. **Rollback Plan**: Test rollback procedures regularly

## Support

For issues with workflows:
1. Check this documentation
2. Review workflow logs in GitHub Actions
3. Verify secret configuration
4. Test deployment scripts manually
5. Check server logs and configuration

Remember: The linting warnings about context access are false positives and can be safely ignored.
# CI/CD Pipeline Test - Mon Sep 29 16:21:34 +0330 2025
