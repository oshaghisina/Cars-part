#!/bin/bash

# Production Monitoring Script for China Car Parts
# This script provides comprehensive monitoring and alerting for production environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROD_DIR="/opt/china-car-parts"
LOG_FILE="/var/log/china-car-parts-monitor.log"
ALERT_LOG="/var/log/china-car-parts-alerts.log"
API_URL="https://yourdomain.com"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
EMAIL_ALERTS="${EMAIL_ALERTS:-false}"
ALERT_THRESHOLD_RESPONSE_TIME=2.0
ALERT_THRESHOLD_ERROR_RATE=5.0
ALERT_THRESHOLD_CPU=80.0
ALERT_THRESHOLD_MEMORY=85.0
ALERT_THRESHOLD_DISK=90.0

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a $LOG_FILE
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a $LOG_FILE
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a $LOG_FILE
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a $LOG_FILE
}

# Send alert function
send_alert() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Log alert
    echo "[$timestamp] [$level] $message" >> $ALERT_LOG
    
    # Send to Slack if webhook is configured
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        local color="good"
        case $level in
            "CRITICAL") color="danger" ;;
            "WARNING") color="warning" ;;
            "INFO") color="good" ;;
        esac
        
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"attachments\":[{\"color\":\"$color\",\"title\":\"China Car Parts Production Alert\",\"text\":\"$message\",\"footer\":\"Production Monitor\",\"ts\":$(date +%s)}]}" \
            $SLACK_WEBHOOK_URL > /dev/null 2>&1 || true
    fi
    
    # Send email if configured
    if [ "$EMAIL_ALERTS" = "true" ]; then
        echo "$message" | mail -s "China Car Parts Production Alert - $level" admin@yourdomain.com > /dev/null 2>&1 || true
    fi
}

# Check API health
check_api_health() {
    log "🩺 Checking API health..."
    
    local response_time
    local http_status
    local health_status="healthy"
    
    # Check response time and status
    response_time=$(curl -w "%{time_total}" -s -o /dev/null "$API_URL/api/v1/health" || echo "999")
    http_status=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/v1/health" || echo "000")
    
    # Check if response time is within threshold
    if (( $(echo "$response_time > $ALERT_THRESHOLD_RESPONSE_TIME" | bc -l) )); then
        warning "API response time is high: ${response_time}s"
        health_status="degraded"
    fi
    
    # Check if HTTP status is OK
    if [ "$http_status" != "200" ]; then
        error "API health check failed with status: $http_status"
        send_alert "CRITICAL" "API health check failed with HTTP status $http_status"
        health_status="unhealthy"
    fi
    
    # Check API health endpoint
    local api_health_response=$(curl -s "$API_URL/api/v1/health" || echo "{}")
    local db_status=$(echo "$api_health_response" | jq -r '.database_status' 2>/dev/null || echo "unknown")
    
    if [ "$db_status" != "healthy" ]; then
        warning "Database status: $db_status"
        health_status="degraded"
    fi
    
    echo "$health_status"
}

# Check service status
check_service_status() {
    log "🔧 Checking service status..."
    
    local current_env=$(cat "$PROD_DIR/.environment" 2>/dev/null || echo "blue")
    local api_status=$(systemctl is-active "china-car-parts-api-$current_env" 2>/dev/null || echo "inactive")
    local bot_status=$(systemctl is-active "china-car-parts-bot-$current_env" 2>/dev/null || echo "inactive")
    local nginx_status=$(systemctl is-active nginx 2>/dev/null || echo "inactive")
    
    # Check API service
    if [ "$api_status" != "active" ]; then
        error "API service is not active: $api_status"
        send_alert "CRITICAL" "API service is not active (status: $api_status)"
        return 1
    fi
    
    # Check Bot service
    if [ "$bot_status" != "active" ]; then
        warning "Bot service is not active: $bot_status"
        send_alert "WARNING" "Bot service is not active (status: $bot_status)"
    fi
    
    # Check Nginx
    if [ "$nginx_status" != "active" ]; then
        error "Nginx is not active: $nginx_status"
        send_alert "CRITICAL" "Nginx is not active (status: $nginx_status)"
        return 1
    fi
    
    success "All services are active"
    return 0
}

# Check system resources
check_system_resources() {
    log "💻 Checking system resources..."
    
    # Check CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    if (( $(echo "$cpu_usage > $ALERT_THRESHOLD_CPU" | bc -l) )); then
        warning "High CPU usage: ${cpu_usage}%"
        send_alert "WARNING" "High CPU usage: ${cpu_usage}%"
    fi
    
    # Check memory usage
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    if (( $(echo "$memory_usage > $ALERT_THRESHOLD_MEMORY" | bc -l) )); then
        warning "High memory usage: ${memory_usage}%"
        send_alert "WARNING" "High memory usage: ${memory_usage}%"
    fi
    
    # Check disk usage
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt "${ALERT_THRESHOLD_DISK%.*}" ]; then
        warning "High disk usage: ${disk_usage}%"
        send_alert "WARNING" "High disk usage: ${disk_usage}%"
    fi
    
    success "System resources check completed"
}

# Check database connectivity
check_database() {
    log "🗄️ Checking database connectivity..."
    
    # Check PostgreSQL status
    local postgres_status=$(systemctl is-active postgresql 2>/dev/null || echo "inactive")
    if [ "$postgres_status" != "active" ]; then
        error "PostgreSQL is not active: $postgres_status"
        send_alert "CRITICAL" "PostgreSQL is not active (status: $postgres_status)"
        return 1
    fi
    
    # Check database connections
    local db_connections=$(sudo -u postgres psql -t -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null || echo "0")
    if [ "$db_connections" -gt 100 ]; then
        warning "High number of database connections: $db_connections"
        send_alert "WARNING" "High number of database connections: $db_connections"
    fi
    
    success "Database connectivity check completed"
}

# Check error rates
check_error_rates() {
    log "📊 Checking error rates..."
    
    # Check recent error logs
    local error_count=$(journalctl -u "china-car-parts-api-*" --since "5 minutes ago" | grep -i error | wc -l)
    local total_requests=$(journalctl -u "china-car-parts-api-*" --since "5 minutes ago" | grep "POST\|GET" | wc -l)
    
    if [ "$total_requests" -gt 0 ]; then
        local error_rate=$(echo "scale=2; $error_count * 100 / $total_requests" | bc)
        
        if (( $(echo "$error_rate > $ALERT_THRESHOLD_ERROR_RATE" | bc -l) )); then
            warning "High error rate: ${error_rate}%"
            send_alert "WARNING" "High error rate: ${error_rate}% ($error_count errors out of $total_requests requests)"
        fi
    fi
    
    success "Error rate check completed"
}

# Check SSL certificate
check_ssl_certificate() {
    log "🔒 Checking SSL certificate..."
    
    local cert_expiry=$(echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates | grep notAfter | cut -d= -f2)
    local cert_expiry_timestamp=$(date -d "$cert_expiry" +%s)
    local current_timestamp=$(date +%s)
    local days_until_expiry=$(( (cert_expiry_timestamp - current_timestamp) / 86400 ))
    
    if [ "$days_until_expiry" -lt 30 ]; then
        warning "SSL certificate expires in $days_until_expiry days"
        send_alert "WARNING" "SSL certificate expires in $days_until_expiry days"
    fi
    
    success "SSL certificate check completed"
}

# Generate monitoring report
generate_report() {
    log "📋 Generating monitoring report..."
    
    local report_file="/var/log/china-car-parts-monitoring-report-$(date +%Y%m%d-%H%M%S).txt"
    
    {
        echo "China Car Parts Production Monitoring Report"
        echo "Generated: $(date)"
        echo "=============================================="
        echo ""
        
        echo "System Status:"
        echo "  CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')"
        echo "  Memory Usage: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
        echo "  Disk Usage: $(df / | tail -1 | awk '{print $5}')"
        echo ""
        
        echo "Service Status:"
        local current_env=$(cat "$PROD_DIR/.environment" 2>/dev/null || echo "blue")
        echo "  Current Environment: $current_env"
        echo "  API Service: $(systemctl is-active "china-car-parts-api-$current_env" 2>/dev/null || echo 'inactive')"
        echo "  Bot Service: $(systemctl is-active "china-car-parts-bot-$current_env" 2>/dev/null || echo 'inactive')"
        echo "  Nginx: $(systemctl is-active nginx 2>/dev/null || echo 'inactive')"
        echo "  PostgreSQL: $(systemctl is-active postgresql 2>/dev/null || echo 'inactive')"
        echo ""
        
        echo "API Health:"
        local api_health=$(check_api_health)
        echo "  Status: $api_health"
        echo "  Response Time: $(curl -w "%{time_total}" -s -o /dev/null "$API_URL/api/v1/health" || echo "N/A")s"
        echo ""
        
        echo "Recent Alerts:"
        tail -10 "$ALERT_LOG" 2>/dev/null || echo "No recent alerts"
        
    } > "$report_file"
    
    success "Monitoring report generated: $report_file"
}

# Main monitoring function
monitor() {
    log "🔍 Starting production monitoring..."
    
    local overall_status="healthy"
    
    # Run all checks
    if ! check_service_status; then
        overall_status="critical"
    fi
    
    local api_health=$(check_api_health)
    if [ "$api_health" != "healthy" ]; then
        overall_status="degraded"
    fi
    
    check_system_resources
    check_database
    check_error_rates
    check_ssl_certificate
    
    # Generate report
    generate_report
    
    # Log overall status
    case $overall_status in
        "healthy")
            success "Production monitoring completed - All systems healthy"
            ;;
        "degraded")
            warning "Production monitoring completed - Some systems degraded"
            ;;
        "critical")
            error "Production monitoring completed - Critical issues detected"
            ;;
    esac
    
    return 0
}

# Show help
show_help() {
    echo "Production Monitoring Script for China Car Parts"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -m, --monitor              Run full monitoring check"
    echo "  -h, --health               Check API health only"
    echo "  -s, --services             Check service status only"
    echo "  -r, --resources            Check system resources only"
    echo "  -d, --database             Check database connectivity only"
    echo "  -e, --errors               Check error rates only"
    echo "  -c, --certificate          Check SSL certificate only"
    echo "  -g, --generate-report      Generate monitoring report"
    echo "  --help                     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --monitor"
    echo "  $0 --health"
    echo "  $0 --services"
}

# Main execution
main() {
    # Create log directories if they don't exist
    mkdir -p "$(dirname "$LOG_FILE")"
    mkdir -p "$(dirname "$ALERT_LOG")"
    
    case "${1:-}" in
        -m|--monitor)
            monitor
            ;;
        -h|--health)
            check_api_health
            ;;
        -s|--services)
            check_service_status
            ;;
        -r|--resources)
            check_system_resources
            ;;
        -d|--database)
            check_database
            ;;
        -e|--errors)
            check_error_rates
            ;;
        -c|--certificate)
            check_ssl_certificate
            ;;
        -g|--generate-report)
            generate_report
            ;;
        --help)
            show_help
            ;;
        "")
            monitor
            ;;
        *)
            error "Unknown option: $1. Use --help for usage information."
            ;;
    esac
}

# Run main function
main "$@"
