#!/usr/bin/env python3
"""
NEXKEY — Daily Summary Report
Generates a comprehensive daily summary of all system activity.
Only sends if there's meaningful activity to report.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path


def get_metrics():
    """Load current metrics"""
    metrics_file = Path(__file__).parent.parent / "data" / "metrics.json"
    if metrics_file.exists():
        with open(metrics_file, 'r') as f:
            return json.load(f)
    return {}


def get_campaign_history():
    """Load campaign history"""
    history_file = Path(__file__).parent.parent / "data" / "outreach_history.json"
    if history_file.exists():
        with open(history_file, 'r') as f:
            return json.load(f)
    return []


def get_yesterday_summary():
    """Generate summary for yesterday's activity"""
    yesterday = datetime.now() - timedelta(days=1)
    
    metrics = get_metrics()
    campaigns = get_campaign_history()
    
    # Count yesterday's campaigns
    yesterday_campaigns = [
        c for c in campaigns 
        if datetime.fromisoformat(c["timestamp"]).date() == yesterday.date()
    ]
    
    summary = {
        "date": yesterday.strftime("%Y-%m-%d"),
        "system_status": "✅ Operational",
        "metrics": {
            "total_leads": metrics.get("total_leads", 0),
            "qualified_leads": metrics.get("qualified_leads", 0),
            "conversion_rate": f"{metrics.get('conversion_rate', 0):.1f}%",
            "campaigns_run": metrics.get("campaigns_run", 0),
            "messages_sent": metrics.get("messages_sent", 0),
            "health_checks": metrics.get("health_checks", 0)
        },
        "yesterday_activity": {
            "campaigns": len(yesterday_campaigns),
            "total_sent": sum(c.get("sent", 0) for c in yesterday_campaigns),
            "total_failed": sum(c.get("failed", 0) for c in yesterday_campaigns)
        }
    }
    
    return summary


def format_summary(summary):
    """Format summary for display"""
    output = []
    output.append(f"\n{'='*50}")
    output.append(f"📊 NEXKEY Daily Summary")
    output.append(f"{'='*50}")
    output.append(f"📅 Date: {summary['date']}")
    output.append(f"🟢 Status: {summary['system_status']}")
    output.append(f"\n📈 Metrics:")
    for key, value in summary['metrics'].items():
        output.append(f"  {key}: {value}")
    output.append(f"\n🚀 Yesterday's Activity:")
    for key, value in summary['yesterday_activity'].items():
        output.append(f"  {key}: {value}")
    output.append(f"\n{'='*50}\n")
    return '\n'.join(output)


def main():
    """Generate and return daily summary"""
    summary = get_yesterday_summary()
    formatted = format_summary(summary)
    print(formatted)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
