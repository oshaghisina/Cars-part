# 🚀 Production Deployment Fix

## ❌ **Problem Identified**

The production deployment failed with this error:
```
/tmp/deploy-blue-green.sh: line 15: cd: /opt/china-car-parts-blue: No such file or directory
```

## 🔍 **Root Cause**

The GitHub Actions workflow is trying to deploy to blue-green environments, but the production server doesn't have the required directory structure set up yet. The script expects:

- `/opt/china-car-parts-blue/` - Blue environment directory
- `/opt/china-car-parts-green/` - Green environment directory

But these directories don't exist on the production server.

## ✅ **Solution**

### **Step 1: Run Setup Script on Production Server**

You need to run the setup script **ONCE** on your production server before the first deployment:

```bash
# On your production server (5.223.59.155)
sudo ./setup_production_blue_green.sh
```

This script will:
- ✅ Create the required directories (`/opt/china-car-parts-blue`, `/opt/china-car-parts-green`)
- ✅ Clone the repository to both environments
- ✅ Set up Python virtual environments
- ✅ Configure systemd services for both blue and green
- ✅ Set up Nginx with load balancing
- ✅ Create environment configuration files
- ✅ Start the initial blue environment

### **Step 2: Update Configuration**

After running the setup script, you need to update the configuration files:

1. **Update Repository URL** in `setup_production_blue_green.sh`:
   ```bash
   REPO_URL="https://github.com/YOUR_USERNAME/china-car-parts.git"
   ```

2. **Update Environment Variables** in both:
   - `/opt/china-car-parts-blue/.env`
   - `/opt/china-car-parts-green/.env`
   
   Set these values:
   ```bash
   TELEGRAM_BOT_TOKEN=your_actual_bot_token
   ADMIN_TELEGRAM_IDS=your_telegram_user_id
   OPENAI_API_KEY=your_openai_api_key
   SECRET_KEY=your_32_character_secret_key
   JWT_SECRET_KEY=your_32_character_jwt_secret_key
   ```

3. **Update Domain Name** in Nginx configuration:
   ```bash
   sudo nano /etc/nginx/sites-available/china-car-parts
   # Replace 'yourdomain.com' with your actual domain
   ```

### **Step 3: Test the Setup**

After running the setup script, test that everything works:

```bash
# Check if directories exist
ls -la /opt/china-car-parts-*

# Check if services are running
systemctl status china-car-parts-api-blue
systemctl status china-car-parts-bot-blue

# Test API health
curl http://localhost:8001/api/v1/health

# Test through Nginx (if domain is configured)
curl http://yourdomain.com/api/v1/health
```

### **Step 4: Deploy via GitHub Actions**

Once the setup is complete, you can deploy via GitHub Actions:

1. **Push to main branch** - This will trigger the production deployment
2. **Monitor the deployment** in GitHub Actions
3. **Check the logs** if there are any issues

## 🔧 **Manual Commands for Production Server**

If you need to manually manage the services:

```bash
# Check service status
systemctl status china-car-parts-api-blue
systemctl status china-car-parts-api-green
systemctl status china-car-parts-bot-blue
systemctl status china-car-parts-bot-green

# View logs
journalctl -u china-car-parts-api-blue -f
journalctl -u china-car-parts-bot-blue -f

# Restart services
systemctl restart china-car-parts-api-blue
systemctl restart china-car-parts-bot-blue

# Check Nginx status
systemctl status nginx
nginx -t  # Test configuration

# Reload Nginx
systemctl reload nginx
```

## 📋 **Files Created/Modified**

1. **`setup_production_blue_green.sh`** - New setup script for production server
2. **`.github/workflows/main_password_auth.yml`** - Updated with better error handling

## 🚨 **Important Notes**

- ⚠️ **Run the setup script ONLY ONCE** on the production server
- ⚠️ **Update the repository URL** in the setup script before running it
- ⚠️ **Configure environment variables** after running the setup
- ⚠️ **Set up SSL certificates** with Certbot after the basic setup
- ⚠️ **Test the deployment** before going live

## 🎯 **Next Steps**

1. **Run the setup script** on your production server
2. **Update the configuration** with your actual values
3. **Test the setup** locally
4. **Deploy via GitHub Actions** by pushing to main branch
5. **Monitor the deployment** and fix any issues

## 📞 **Support**

If you encounter any issues:

1. Check the logs: `journalctl -u china-car-parts-api-blue -f`
2. Verify the setup: `ls -la /opt/china-car-parts-*`
3. Test the API: `curl http://localhost:8001/api/v1/health`
4. Check Nginx: `nginx -t && systemctl status nginx`

The deployment should work after running the setup script! 🚀
