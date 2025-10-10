#!/usr/bin/env bash
set -euo pipefail
n=${1:-"0002"}
title=${2:-"decision-title"}
date=$(date +%F)
dir="docs/adr"
mkdir -p "$dir"
file="$dir/ADR-${n}-${title// /-}.md"
cat > "$file" <<'EOT'
# ADR-${n}: ${title}
Date: ${date}
## Status
Proposed
## Context
## Decision
## Consequences
## References
EOT

echo "Created $file"
