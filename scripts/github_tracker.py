import os, requests
from dotenv import load_dotenv

load_dotenv()

def create_account_issue(account_id: str, company_name: str, version: str):
    """Create a GitHub issue for the account as a tracking item."""
    url = f"https://api.github.com/repos/{os.environ['GITHUB_REPO']}/issues"
    headers = {
        "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
        "Content-Type": "application/json"
    }
    payload = {
        "title": f"[{version.upper()}] {company_name} ({account_id})",
        "body": f"Account {account_id} processed.\n- Version: {version}\n- Status: Awaiting onboarding" if version == "v1" else f"Onboarding complete for {account_id}.",
        "labels": ["clara-account", version]
    }
    r = requests.post(url, json=payload, headers=headers)
    return r.json().get("html_url")