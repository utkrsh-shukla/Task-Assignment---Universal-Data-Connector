"""Mock data generators for CRM, support, and analytics."""

import json, random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List
from app.config import settings

_FIRST = ["Alice","Bob","Charlie","Diana","Ethan","Fiona","George",
          "Hannah","Ivan","Julia","Kevin","Laura","Mike","Nina",
          "Oscar","Priya","Quinn","Rachel","Sam","Tina"]
_LAST = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller",
         "Davis","Rodriguez","Martinez","Hernandez","Lopez","Wilson",
         "Anderson","Thomas","Taylor","Moore","Jackson"]
_SUBJECTS = [
    "Cannot log in to dashboard","Billing discrepancy on invoice",
    "Feature request: dark mode","API rate limit exceeded","Data export failed",
    "Mobile app crashing on launch","Password reset not working",
    "Integration with Slack broken","Slow page load times",
    "Missing data in reports","SSO configuration help needed",
    "Webhook delivery failures","Account upgrade request",
    "Permission error on admin panel","Custom domain setup assistance",
]


def generate_customers(count: int = 50) -> List[Dict[str, Any]]:
    now = datetime.utcnow()
    return [{"customer_id": i,
             "name": f"{random.choice(_FIRST)} {random.choice(_LAST)}",
             "email": f"{random.choice(_FIRST).lower()}.{random.choice(_LAST).lower()}{i}@example.com",
             "created_at": (now - timedelta(days=random.randint(1, 365))).isoformat(),
             "status": random.choice(["active", "inactive"])}
            for i in range(1, count + 1)]


def generate_support_tickets(count: int = 50, max_cid: int = 50) -> List[Dict[str, Any]]:
    now = datetime.utcnow()
    return [{"ticket_id": i,
             "customer_id": random.randint(1, max_cid),
             "subject": random.choice(_SUBJECTS),
             "priority": random.choice(["high", "medium", "low"]),
             "created_at": (now - timedelta(days=random.randint(0, 30))).isoformat(),
             "status": random.choice(["open", "closed"])}
            for i in range(1, count + 1)]


def generate_analytics(days: int = 30) -> List[Dict[str, Any]]:
    today = datetime.utcnow().date()
    return [{"metric": "daily_active_users",
             "date": (today - timedelta(days=d)).isoformat(),
             "value": random.randint(100, 1000)}
            for d in range(days)]


def write_mock_data(output_dir: str | None = None, customer_count: int = 50):
    out = Path(output_dir or settings.DATA_DIR)
    out.mkdir(parents=True, exist_ok=True)
    for name, data in [("customers.json", generate_customers(customer_count)),
                       ("support_tickets.json", generate_support_tickets(customer_count, customer_count)),
                       ("analytics.json", generate_analytics(30))]:
        with open(out / name, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Wrote {len(data)} records to {out / name}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Generate mock data")
    p.add_argument("--count", type=int, default=50)
    write_mock_data(customer_count=p.parse_args().count)
