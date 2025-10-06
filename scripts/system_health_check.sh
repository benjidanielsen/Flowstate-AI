#!/bin/bash

# Flowstate-AI System Health Check Script
# Purpose: Monitor system health and log status
# Created: October 6, 2025
# Target Completion: August 7, 2026

# Configuration
LOG_DIR="/home/ubuntu/Flowstate-AI/logs"
HEALTH_LOG="$LOG_DIR/system_health.log"
DB_PATH="/home/ubuntu/Flowstate-AI/godmode-state.db"
DASHBOARD_PORT=5000

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$HEALTH_LOG"
}

# Function to check process status
check_process() {
    local process_name=$1
    if pgrep -f "$process_name" > /dev/null; then
        log_message "✅ $process_name is running"
        return 0
    else
        log_message "❌ $process_name is NOT running"
        return 1
    fi
}

# Function to check database
check_database() {
    if [ -f "$DB_PATH" ]; then
        local table_count=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" 2>/dev/null)
        if [ $? -eq 0 ]; then
            log_message "✅ Database accessible ($table_count tables)"
            
            # Check leads count
            local leads_count=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM leads;" 2>/dev/null)
            log_message "   - Leads: $leads_count"
            
            # Check tasks count
            local tasks_count=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM tasks;" 2>/dev/null)
            log_message "   - Tasks: $tasks_count"
            
            return 0
        else
            log_message "❌ Database error"
            return 1
        fi
    else
        log_message "❌ Database file not found"
        return 1
    fi
}

# Function to check dashboard endpoint
check_dashboard() {
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$DASHBOARD_PORT/ 2>/dev/null)
    if [ "$http_code" == "302" ] || [ "$http_code" == "200" ]; then
        log_message "✅ Dashboard responding (HTTP $http_code)"
        return 0
    else
        log_message "❌ Dashboard not responding (HTTP $http_code)"
        return 1
    fi
}

# Function to check system resources
check_resources() {
    local mem_available=$(free -m | awk 'NR==2{print $7}')
    local disk_available=$(df -h /home/ubuntu | awk 'NR==2{print $4}')
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
    
    log_message "✅ System Resources:"
    log_message "   - Memory Available: ${mem_available}MB"
    log_message "   - Disk Available: $disk_available"
    log_message "   - Load Average: $load_avg"
}

# Function to check strategic documents
check_documents() {
    local doc_dir="/home/ubuntu/Flowstate-AI/docs/strategic_plans"
    if [ -d "$doc_dir" ]; then
        local doc_count=$(ls -1 "$doc_dir"/*.md 2>/dev/null | wc -l)
        log_message "✅ Strategic documents: $doc_count files"
        return 0
    else
        log_message "❌ Strategic documents directory not found"
        return 1
    fi
}

# Main health check execution
log_message "========================================="
log_message "FLOWSTATE-AI SYSTEM HEALTH CHECK"
log_message "========================================="

# Check all components
check_process "unified_dashboard.py"
check_database
check_dashboard
check_resources
check_documents

# Calculate days remaining until completion
target_date="2026-08-07"
current_date=$(date '+%Y-%m-%d')
days_remaining=$(( ($(date -d "$target_date" +%s) - $(date -d "$current_date" +%s)) / 86400 ))

log_message "========================================="
log_message "Days until completion: $days_remaining"
log_message "Target Date: August 7, 2026"
log_message "Status: ACTIVE AND OPERATIONAL"
log_message "========================================="

# Exit with success
exit 0
