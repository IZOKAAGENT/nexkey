#!/bin/bash
# NEXKEY Outreach - Silent mode (only reports errors)
cd /opt/data/nexkey
source .venv/bin/activate
python3 scripts/automated_outreach.py 2>&1 | grep -i "error\|fail" && exit 0 || echo "[SILENT]"
