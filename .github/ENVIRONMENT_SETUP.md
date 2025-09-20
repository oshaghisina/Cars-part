# 🔧 GitHub Actions Environment Setup

## Required GitHub Secrets

Configure these secrets in your GitHub repository settings:

### **Staging Environment Secrets**
```
STAGING_SSH_PRIVATE_KEY    # SSH private key for staging server access
STAGING_USER              # Username for staging server (e.g., 'staging')
STAGING_HOST              # Staging server IP or domain
STAGING_API_URL           # Staging API base URL
```

### **Production Environment Secrets**
```
PROD_SSH_PRIVATE_KEY      # SSH private key for production server access
PROD_USER                # Username for production server (e.g., 'production')
PROD_HOST                # Production server IP or domain
PROD_API_URL             # Production API base URL
```

### **General Secrets**
```
DATABASE_URL             # Production database connection string
TELEGRAM_BOT_TOKEN      # Production Telegram bot token
SECRET_KEY              # Application secret key
SLACK_WEBHOOK_URL       # Slack webhook for notifications (optional)
CODECOV_TOKEN           # Codecov token for coverage reporting (optional)
```

## Environment Setup Instructions

### **1. Create SSH Keys**

Generate separate SSH keys for staging and production:

```bash
# Staging SSH key
ssh-keygen -t ed25519 -C "github-actions-staging" -f ~/.ssh/github_staging_key

# Production SSH key
ssh-keygen -t ed25519 -C "github-actions-production" -f ~/.ssh/github_production_key
```

### **2. Configure Server Access**

#### **Staging Server Setup:**
```bash
# On staging server
sudo useradd -m -s /bin/bash staging
sudo mkdir -p /home/staging/.ssh
sudo chmod 700 /home/staging/.ssh

# Add staging public key to authorized_keys
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5... github-actions-staging" | sudo tee -a /home/staging/.ssh/authorized_keys
sudo chmod 600 /home/staging/.ssh/authorized_keys
sudo chown -R staging:staging /home/staging/.ssh

# Configure sudo access for staging user
echo "staging ALL=(ALL) NOPASSWD: /bin/systemctl start china-car-parts-api-staging, /bin/systemctl stop china-car-parts-api-staging, /bin/systemctl restart china-car-parts-api-staging, /bin/systemctl start china-car-parts-bot-staging, /bin/systemctl stop china-car-parts-bot-staging, /bin/systemctl restart china-car-parts-bot-staging, /bin/systemctl reload nginx" | sudo tee /etc/sudoers.d/staging-deploy
```

#### **Production Server Setup:**
```bash
# On production server
sudo useradd -m -s /bin/bash production
sudo mkdir -p /home/production/.ssh
sudo chmod 700 /home/production/.ssh

# Add production public key to authorized_keys
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5... github-actions-production" | sudo tee -a /home/production/.ssh/authorized_keys
sudo chmod 600 /home/production/.ssh/authorized_keys
sudo chown -R production:production /home/production/.ssh

# Configure sudo access for production user
echo "production ALL=(ALL) NOPASSWD: /bin/systemctl start china-car-parts-api, /bin/systemctl stop china-car-parts-api, /bin/systemctl restart china-car-parts-api, /bin/systemctl start china-car-parts-bot, /bin/systemctl stop china-car-parts-bot, /bin/systemctl restart china-car-parts-bot, /bin/systemctl reload nginx" | sudo tee /etc/sudoers.d/production-deploy
```

### **3. Add GitHub Secrets**

In your GitHub repository:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add each secret with the corresponding value

#### **SSH Private Keys:**
- Copy the **private key** content (not public key)
- Include the full key with headers:
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAFwAAAAdzc2gtZ...
-----END OPENSSH PRIVATE KEY-----
```

### **4. Test SSH Connection**

Test the SSH connections manually:

```bash
# Test staging connection
ssh -i ~/.ssh/github_staging_key staging@staging.yourdomain.com

# Test production connection
ssh -i ~/.ssh/github_production_key production@yourdomain.com
```

## Branch Protection Setup

### **1. Enable Branch Protection**

In GitHub repository settings:
1. Go to **Settings** → **Branches**
2. Click **Add rule**
3. Configure for `main` branch:
   - ✅ Require a pull request before merging
   - ✅ Require approvals (2 reviewers)
   - ✅ Dismiss stale PR approvals when new commits are pushed
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Require linear history
   - ✅ Restrict pushes that create files

### **2. Configure Required Status Checks**

For the `main` branch, require these status checks:
- ✅ Backend Tests & Linting
- ✅ Frontend Tests & Build
- ✅ Security Scanning (if enabled)

### **3. Configure Environments**

Create GitHub Environments for deployment protection:

#### **Staging Environment:**
1. Go to **Settings** → **Environments**
2. Click **New environment**
3. Name: `staging`
4. ✅ Required reviewers: Add yourself
5. ✅ Wait timer: 0 minutes
6. ✅ Prevent self-review: No

#### **Production Environment:**
1. Go to **Settings** → **Environments**
2. Click **New environment**
3. Name: `production`
4. ✅ Required reviewers: Add yourself and team lead
5. ✅ Wait timer: 5 minutes
6. ✅ Prevent self-review: Yes

## Verification Checklist

- [ ] All GitHub secrets configured
- [ ] SSH keys generated and deployed to servers
- [ ] Server user accounts created with proper permissions
- [ ] SSH connections tested manually
- [ ] Branch protection rules configured
- [ ] Required status checks specified
- [ ] Environments created with protection rules
- [ ] First test deployment completed successfully

## Troubleshooting

### **SSH Connection Issues:**
```bash
# Check SSH key permissions
chmod 600 ~/.ssh/private_key
chmod 700 ~/.ssh/

# Test with verbose output
ssh -vvv -i ~/.ssh/private_key user@host
```

### **Permission Issues:**
```bash
# Check sudo configuration
sudo -l

# Test specific commands
sudo systemctl status china-car-parts-api
```

### **GitHub Actions Issues:**
- Check secret names match exactly (case-sensitive)
- Verify SSH key format includes headers
- Ensure server firewall allows SSH connections
- Check GitHub Actions logs for detailed error messages
