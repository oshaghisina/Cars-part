# GitHub Secrets Verification Guide

## ✅ Required Secrets Checklist

### Production Secrets
- [ ] `PROD_SSH_PRIVATE_KEY` - SSH private key for production server
- [ ] `PROD_USER` - Username for production server (e.g., `partsbot`)
- [ ] `PROD_HOST` - Production server IP/domain (e.g., `5.223.59.155`)
- [ ] `PROD_API_URL` - Production API URL (e.g., `https://5.223.59.155/api`)
- [ ] `PROD_FRONTEND_ORIGIN` - Production frontend URL (e.g., `https://5.223.59.155`)

### Staging Secrets (Optional)
- [ ] `STAGING_SSH_PRIVATE_KEY` - SSH private key for staging server
- [ ] `STAGING_USER` - Username for staging server
- [ ] `STAGING_HOST` - Staging server IP/domain
- [ ] `STAGING_API_URL` - Staging API URL
- [ ] `STAGING_FRONTEND_ORIGIN` - Staging frontend URL

## 🔧 How to Add Secrets

1. Go to: `https://github.com/oshaghisina/Cars-part/settings/secrets/actions`
2. Click **"New repository secret"**
3. Enter the secret name and value
4. Click **"Add secret"**

## 🧪 Test SSH Connection

Before deploying, test your SSH connection:

```bash
# Test production server connection
ssh -i ~/.ssh/china_car_parts_deploy partsbot@5.223.59.155 "echo 'SSH connection successful'"

# Test staging server connection (if configured)
ssh -i ~/.ssh/china_car_parts_deploy staging@your-staging-server "echo 'SSH connection successful'"
```

## 🚀 After Adding Secrets

Once all secrets are added:

1. **Trigger deployment** by pushing to `main` branch
2. **Monitor deployment** in GitHub Actions tab
3. **Check logs** for any authentication errors
4. **Verify deployment** by accessing the production URLs

## ⚠️ Important Notes

- **Never commit SSH private keys** to your repository
- **Use strong, unique SSH keys** for production
- **Rotate keys regularly** for security
- **Test connections** before deploying
- **Keep secrets secure** and limit access

## 🔍 Troubleshooting

### SSH Connection Issues
- Verify SSH key is correctly added to server's `~/.ssh/authorized_keys`
- Check server firewall allows SSH connections
- Ensure user has proper permissions on the server

### Deployment Failures
- Check GitHub Actions logs for specific error messages
- Verify all required secrets are present
- Test SSH connection manually
- Check server disk space and resources

### Permission Issues
- Ensure the deployment user has sudo access for service management
- Check file permissions in the application directory
- Verify database access permissions
