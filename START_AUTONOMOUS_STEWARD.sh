#!/bin/bash
#
# Autonomous VS Code Project Steward - Startup Script
# Starts the autonomous steward system for continuous repository improvement
#

set -e

echo "🤖 =========================================="
echo "🤖  AUTONOMOUS VS CODE PROJECT STEWARD"
echo "🤖 =========================================="
echo ""

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not found"
    echo "   Please install Python 3.8 or higher"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python version: $PYTHON_VERSION"

# Ensure log directory exists
mkdir -p godmode-logs

# Check if PROGRESS.md exists
if [ ! -f "PROGRESS.md" ]; then
    echo "📝 Creating PROGRESS.md..."
    cat > PROGRESS.md << EOF
# Autonomous Project Steward - Progress Log

This file tracks all autonomous improvements made by the VS Code Project Steward.

---

## $(date '+%Y-%m-%d %H:%M') – Session Start
- Why: Initializing autonomous VS Code project steward system
- Changes: Created PROGRESS.md tracking file
- Commands: Initial repository scan
- Result: Repository structure analyzed, baseline established
- Next: Begin DISCOVER → PLAN → EXECUTE → REPEAT loop

EOF
fi

echo ""
echo "📋 Configuration:"
echo "   - Project Root: $PROJECT_ROOT"
echo "   - Progress Log: PROGRESS.md"
echo "   - System Log: godmode-logs/autonomous-steward.log"
echo ""
echo "🛡️  Safety Rules Active:"
echo "   - No destructive operations (rm -rf, sudo, etc.)"
echo "   - No secrets/credentials handling"
echo "   - No irreversible external effects (publish, deploy)"
echo "   - No resource abuse (jobs >30 min)"
echo ""
echo "🔄 Operating Loop:"
echo "   DISCOVER → PLAN → EXECUTE → REPEAT"
echo ""
echo "⏹️  To stop: Press Ctrl+C"
echo ""
echo "=========================================="
echo "🚀 Starting Autonomous Steward..."
echo "=========================================="
echo ""

# Run the steward
python3 "$PROJECT_ROOT/ai-gods/autonomous_steward.py"

# Cleanup on exit
echo ""
echo "🛑 Autonomous Steward stopped"
echo "📊 Check PROGRESS.md for completed work"
echo "📋 Check godmode-logs/autonomous-steward.log for details"
