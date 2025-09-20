# 🔐 GitHub Secrets Configuration Guide

This guide will help you configure all the necessary secrets for your CI/CD pipeline to deploy to your production server.

## 📋 Required Secrets

### **Core Application Secrets**

#### 1. Database Configuration
```
DATABASE_URL=postgresql://partsbot:china_car_parts_2024!@localhost:5432/china_car_parts
```

#### 2. Telegram Bot Configuration
```
TELEGRAM_BOT_TOKEN=your_actual_telegram_bot_token_here
TELEGRAM_ADMIN_IDS=123456789,987654321
```

#### 3. Security Keys
```
SECRET_KEY=china_car_parts_production_secret_key_2024
JWT_SECRET_KEY=china_car_parts_jwt_secret_key_2024
```

### **Production Server Secrets**

#### 4. SSH Configuration
```
PROD_SSH_PRIVATE_KEY=<your_ssh_private_key_content>
PROD_HOST=5.223.59.155
PROD_USER=root
```

#### 5. Production URLs
```
PROD_API_URL=https://5.223.59.155/api
PROD_FRONTEND_ORIGIN=https://5.223.59.155
```

### **Optional Secrets (for enhanced features)**

#### 6. Security Scanning (Optional)
```
SEMGREP_APP_TOKEN=your_semgrep_token
SNYK_TOKEN=your_snyk_token
GITLEAKS_LICENSE=your_gitleaks_license
```

#### 7. Performance Testing (Optional)
```
LHCI_GITHUB_APP_TOKEN=your_lighthouse_token
```

#### 8. Notifications (Optional)
```
SLACK_WEBHOOK_URL=your_slack_webhook_url
DISCORD_WEBHOOK_URL=your_discord_webhook_url
```

## 🔧 How to Add Secrets to GitHub

### Step 1: Access GitHub Secrets
1. Go to your repository: https://github.com/oshaghisina/Cars-part
2. Click on **Settings** tab
3. In the left sidebar, click on **Secrets and variables**
4. Click on **Actions**

### Step 2: Add Each Secret
1. Click **New repository secret**
2. Enter the **Name** (exactly as shown above)
3. Enter the **Secret** value
4. Click **Add secret**

### Step 3: Verify Secrets
After adding all secrets, you should see them listed in the secrets page.

## 🔑 SSH Key Generation

### Generate SSH Key Pair

On your local machine, run:

```bash
# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -C "china-car-parts-deployment" -f ~/.ssh/china_car_parts_key

# This will create two files:
# ~/.ssh/china_car_parts_key (private key)
# ~/.ssh/china_car_parts_key.pub (public key)
```

### Add Public Key to Server

```bash
# Copy public key to your server
ssh-copy-id -i ~/.ssh/china_car_parts_key.pub root@5.223.59.155

# Test connection
ssh -i ~/.ssh/china_car_parts_key root@5.223.59.155
```

### Add Private Key to GitHub

1. Copy the content of your private key:
   ```bash
   cat ~/.ssh/china_car_parts_key
   ```

2. Add it to GitHub Secrets as `PROD_SSH_PRIVATE_KEY`

## 🤖 Telegram Bot Setup

### Get Telegram Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Follow the instructions to create your bot
4. Copy the bot token

### Get Admin IDs

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. It will reply with your user ID
3. Add your user ID to `TELEGRAM_ADMIN_IDS`

## 📝 Complete Secrets List

Here's the complete list of secrets you need to add:

| Secret Name | Value | Required |
|-------------|-------|----------|
| `DATABASE_URL` | `postgresql://partsbot:china_car_parts_2024!@localhost:5432/china_car_parts` | ✅ |
| `TELEGRAM_BOT_TOKEN` | Your actual bot token from @BotFather | ✅ |
| `TELEGRAM_ADMIN_IDS` | Your Telegram user ID | ✅ |
| `SECRET_KEY` | `china_car_parts_production_secret_key_2024` | ✅ |
| `JWT_SECRET_KEY` | `china_car_parts_jwt_secret_key_2024` | ✅ |
| `PROD_SSH_PRIVATE_KEY` | Content of your SSH private key | ✅ |
| `PROD_HOST` | `5.223.59.155` | ✅ |
| `PROD_USER` | `root` | ✅ |
| `PROD_API_URL` | `https://5.223.59.155/api` | ✅ |
| `PROD_FRONTEND_ORIGIN` | `https://5.223.59.155` | ✅ |
| `SEMGREP_APP_TOKEN` | Your Semgrep token (optional) | ❌ |
| `SNYK_TOKEN` | Your Snyk token (optional) | ❌ |
| `GITLEAKS_LICENSE` | Your GitLeaks license (optional) | ❌ |
| `LHCI_GITHUB_APP_TOKEN` | Your Lighthouse CI token (optional) | ❌ |
| `SLACK_WEBHOOK_URL` | Your Slack webhook URL (optional) | ❌ |
| `DISCORD_WEBHOOK_URL` | Your Discord webhook URL (optional) | ❌ |

## 🧪 Testing Secrets Configuration

### Test SSH Connection

```bash
# Test SSH connection with your key
ssh -i ~/.ssh/china_car_parts_key root@5.223.59.155 "echo 'SSH connection successful'"
```

### Test GitHub Actions

1. Go to your repository Actions tab
2. Click on "CI - China Car Parts" workflow
3. Click "Run workflow" to test
4. Check if all secrets are properly configured

## 🔒 Security Best Practices

### Secret Management
- ✅ Use strong, unique passwords
- ✅ Rotate secrets regularly
- ✅ Never commit secrets to code
- ✅ Use environment-specific secrets
- ✅ Limit secret access permissions

### SSH Key Security
- ✅ Use RSA 4096-bit keys
- ✅ Protect private key with passphrase
- ✅ Regularly rotate SSH keys
- ✅ Use dedicated deployment keys

### Database Security
- ✅ Use strong database passwords
- ✅ Limit database user permissions
- ✅ Enable SSL for database connections
- ✅ Regular database backups

## 🚨 Troubleshooting

### Common Issues

#### 1. SSH Connection Failed
```bash
# Check SSH key permissions
chmod 600 ~/.ssh/china_car_parts_key

# Test SSH connection
ssh -v -i ~/.ssh/china_car_parts_key root@5.223.59.155
```

#### 2. GitHub Actions Fails
- Check if all required secrets are added
- Verify secret names match exactly
- Check secret values for typos
- Review GitHub Actions logs

#### 3. Database Connection Issues
- Verify database credentials
- Check if PostgreSQL is running
- Test database connection manually

#### 4. Telegram Bot Issues
- Verify bot token is correct
- Check if bot is active
- Test bot with /start command

## 📞 Support

If you encounter issues:

1. **Check GitHub Actions logs** for specific error messages
2. **Verify all secrets** are correctly configured
3. **Test SSH connection** manually
4. **Review server setup** guide
5. **Check firewall rules** on your server

## 🎯 Next Steps

After configuring all secrets:

1. **Run server setup script** on your production server
2. **Test CI/CD pipeline** with a test deployment
3. **Verify all services** are running correctly
4. **Set up monitoring** and logging
5. **Configure SSL certificate** for HTTPS

---

**Your GitHub Secrets are now configured for CI/CD deployment! 🚀**
