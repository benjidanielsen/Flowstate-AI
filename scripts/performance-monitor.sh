#!/bin/bash

# Flowstate-AI Performance Monitoring Script
# Monitors system performance and generates reports

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default values
DURATION=60
OUTPUT_DIR="./performance-reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$OUTPUT_DIR/performance_$TIMESTAMP.txt"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--duration)
            DURATION="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [-d|--duration SECONDS] [-o|--output DIR]"
            exit 1
            ;;
    esac
done

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}📊 Flowstate-AI Performance Monitor${NC}"
echo "====================================="
echo "Duration: ${DURATION}s"
echo "Output: $REPORT_FILE"
echo ""

# Start monitoring
{
    echo "Flowstate-AI Performance Report"
    echo "Generated: $(date)"
    echo "Duration: ${DURATION}s"
    echo "================================"
    echo ""
    
    # System information
    echo "## System Information"
    echo "-------------------"
    echo "OS: $(uname -s) $(uname -r)"
    echo "CPU: $(grep 'model name' /proc/cpuinfo | head -1 | cut -d':' -f2 | xargs)"
    echo "CPU Cores: $(nproc)"
    echo "Total Memory: $(free -h | awk '/^Mem:/ {print $2}')"
    echo ""
    
    # Docker containers (if running)
    if docker ps &> /dev/null && [ $(docker ps -q | wc -l) -gt 0 ]; then
        echo "## Docker Containers"
        echo "-------------------"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Size}}"
        echo ""
        
        echo "## Container Resource Usage"
        echo "--------------------------"
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
        echo ""
    fi
    
    # CPU Usage
    echo "## CPU Usage Over Time"
    echo "---------------------"
    echo "Sampling every 5 seconds for ${DURATION}s..."
    for i in $(seq 1 $((DURATION / 5))); do
        CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
        echo "Sample $i: ${CPU}%"
        sleep 5
    done
    echo ""
    
    # Memory Usage
    echo "## Memory Usage"
    echo "--------------"
    free -h
    echo ""
    
    # Disk Usage
    echo "## Disk Usage"
    echo "------------"
    df -h | grep -E '^/dev/'
    echo ""
    
    # Network Statistics
    echo "## Network Statistics"
    echo "--------------------"
    if command -v ss &> /dev/null; then
        echo "Active connections:"
        ss -s
    else
        echo "netstat not available"
    fi
    echo ""
    
    # Process Information
    echo "## Top Processes by CPU"
    echo "----------------------"
    ps aux --sort=-%cpu | head -11
    echo ""
    
    echo "## Top Processes by Memory"
    echo "-------------------------"
    ps aux --sort=-%mem | head -11
    echo ""
    
    # Application-specific metrics
    if docker ps --format '{{.Names}}' | grep -q "flowstate-backend"; then
        echo "## Backend Metrics"
        echo "-----------------"
        curl -s http://localhost:3001/metrics 2>/dev/null || echo "Metrics endpoint not available"
        echo ""
    fi
    
    if docker ps --format '{{.Names}}' | grep -q "flowstate-python-worker"; then
        echo "## Python Worker Metrics"
        echo "-----------------------"
        curl -s http://localhost:8000/metrics 2>/dev/null || echo "Metrics endpoint not available"
        echo ""
    fi
    
    # Database statistics (if PostgreSQL is running)
    if docker ps --format '{{.Names}}' | grep -q "flowstate-postgres"; then
        echo "## Database Statistics"
        echo "---------------------"
        docker exec flowstate-postgres psql -U flowstate -d flowstate -c "
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
            FROM pg_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 10;
        " 2>/dev/null || echo "Database statistics not available"
        echo ""
    fi
    
    # Summary
    echo "## Performance Summary"
    echo "---------------------"
    echo "Report completed at: $(date)"
    echo "Total monitoring duration: ${DURATION}s"
    echo ""
    
} > "$REPORT_FILE"

echo -e "${GREEN}✅ Performance report generated${NC}"
echo "Report saved to: $REPORT_FILE"
echo ""
echo "Summary:"
cat "$REPORT_FILE" | grep -A 20 "## Performance Summary"
echo ""

