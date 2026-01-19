"""Lightweight alerting helpers for evaluation (Slack webhook + console)."""
import json
import urllib.request
from typing import Optional


def send_slack_webhook(webhook_url: str, message: str) -> bool:
    payload = {"text": message}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(webhook_url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.getcode() == 200
    except Exception:
        return False


def console_alert(tool: str, alert: dict) -> None:
    print(f"[ALERT] tool={tool} alert={alert}")


def notifier_from_env(slack_webhook: Optional[str]):
    """Return a notifier callable based on environment configuration."""
    if slack_webhook:
        return lambda tool, alert: send_slack_webhook(slack_webhook, f"Budget alert for {tool}: {alert}")
    return lambda tool, alert: console_alert(tool, alert)
