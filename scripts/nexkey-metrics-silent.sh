#!/bin/bash
# NEXKEY Metrics - Silent mode (only reports issues)
cd /opt/data/nexkey
source .venv/bin/activate
python3 scripts/metrics_collector.py 2>&1 | grep -i "error\|fail\|critical" && exit 0 || echo "[SILENT]"
