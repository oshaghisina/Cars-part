# 🔐 GitHub Actions Secrets Setup (Password Authentication)

## Quick Setup Guide

### Step 1: Add GitHub Secrets

Go to: `https://github.com/oshaghisina/Cars-part/settings/secrets/actions`

Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `PROD_SSH_PASSWORD` | `your_server_password` | Password for production server (5.223.59.155) |
| `PROD_USER` | `root` | Username for production server |
| `PROD_HOST` | `5.223.59.155` | Production server IP |
| `PROD_API_URL` | `https://5.223.59.155/api` | Production API URL |
| `PROD_FRONTEND_ORIGIN` | `https://5.223.59.155` | Production frontend URL |

### Step 2: Optional Staging Secrets

If you have a staging server:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `STAGING_SSH_PASSWORD` | `staging_password` | Password for staging server |
| `STAGING_USER` | `root` | Username for staging server |
| `STAGING_HOST` | `your-staging-server.com` | Staging server IP/domain |
| `STAGING_API_URL` | `http://your-staging-server:8001` | Staging API URL |
| `STAGING_FRONTEND_ORIGIN` | `http://your-staging-server:5173` | Staging frontend URL |

## How to Add Secrets

1. **Go to GitHub Repository Settings**
   - Navigate to: `https://github.com/oshaghisina/Cars-part`
   - Click **"Settings"** tab
   - Click **"Secrets and variables"** → **"Actions"**

2. **Add Each Secret**
   - Click **"New repository secret"**
   - Enter the secret name (e.g., `PROD_SSH_PASSWORD`)
   - Enter the secret value (e.g., your server password)
   - Click **"Add secret"**

3. **Repeat for All Secrets**
   - Add all 5 production secrets
   - Add staging secrets if you have a staging server

## Test Connection

Before deploying, test your server connection:

```bash
# Test production server connection
ssh root@5.223.59.155 "echo 'SSH connection successful'"

# Test with password (if prompted)
ssh root@5.223.59.155
# Enter password when prompted
```

## Deploy

Once all secrets are added:

1. **Push to main branch** to trigger production deployment
2. **Push to staging branch** to trigger staging deployment
3. **Monitor deployment** in GitHub Actions tab

## Security Notes

- **Use strong passwords** for your server
- **Limit server access** to necessary users only
- **Consider using SSH keys** for better security in the future
- **Rotate passwords regularly**

## Troubleshooting

### Connection Issues
- Verify server IP and credentials
- Check if SSH is enabled on the server
- Ensure firewall allows SSH connections (port 22)

### Deployment Failures
- Check GitHub Actions logs for specific errors
- Verify all required secrets are present
- Test SSH connection manually
- Check server disk space and resources

### Permission Issues
- Ensure the user has sudo access
- Check file permissions in the application directory
- Verify database access permissions

## Next Steps

After successful deployment:

1. **Test Production URLs**:
   - API: `https://5.223.59.155/api/v1/health`
   - Frontend: `https://5.223.59.155`

2. **Monitor Logs**:
   - Check server logs for any issues
   - Monitor GitHub Actions for deployment status

3. **Set up Monitoring**:
   - Consider setting up uptime monitoring
   - Configure log aggregation
   - Set up alerts for failures
