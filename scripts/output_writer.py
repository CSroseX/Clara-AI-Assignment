import os, json

def write_outputs(account_id: str, version: str, memo: dict, agent_spec: dict, changelog: dict = None):
    base = f"outputs/accounts/{account_id}/{version}"
    os.makedirs(base, exist_ok=True)
    with open(f"{base}/account_memo.json", "w") as f:
        json.dump(memo, f, indent=2)
    with open(f"{base}/agent_spec.json", "w") as f:
        json.dump(agent_spec, f, indent=2)
    if changelog:
        with open(f"{base}/changelog.json", "w") as f:
            json.dump(changelog, f, indent=2)
    # Also append to global changelog
    global_path = "changelog/all_changes.json"
    existing = []
    if os.path.exists(global_path):
        with open(global_path) as f:
            existing = json.load(f)
    existing.append(changelog)
    with open(global_path, "w") as f:
        json.dump(existing, f, indent=2)