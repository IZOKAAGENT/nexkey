#!/bin/bash
# NEXKEY Health Check - Silent mode (only reports errors)
cd /opt/data/nexkey
source .venv/bin/activate
python3 scripts/health_check.py 2>&1 | grep -i "error\|fail\|down" && exit 0 || echo "[SILENT]"
