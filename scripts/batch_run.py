import os, json, glob
from normalize import normalize_transcript
from extract import extract_account_memo
from prompt_generator import generate_agent_spec
from patch import apply_patch
from supabase_client import upsert_account_v1, upsert_account_v2
from github_tracker import create_account_issue
from output_writer import write_outputs

def run_pipeline_a(filepath: str):
    """Demo call → v1 memo + agent spec."""
    print(f"[Pipeline A] Processing {filepath}")
    transcript = normalize_transcript(filepath)
    memo = extract_account_memo(transcript)
    agent = generate_agent_spec(memo, version="v1")
    write_outputs(memo["account_id"], "v1", memo, agent)
    upsert_account_v1(memo, agent)
    url = create_account_issue(memo["account_id"], memo.get("company_name", "Unknown"), "v1")
    print(f" ✓ v1 complete | Issue: {url}")

def run_pipeline_b(filepath: str):
    """Onboarding call → v2 patch + changelog."""
    print(f"[Pipeline B] Processing {filepath}")
    transcript = normalize_transcript(filepath)
    updates = extract_account_memo(transcript)  # Extract only what changed
    account_id = transcript["account_id"].replace("onboarding_", "demo_")
    v1_path = f"outputs/accounts/{account_id}/v1/account_memo.json"
    with open(v1_path) as f:
        v1_memo = json.load(f)
    v2_memo, changelog = apply_patch(v1_memo, updates)
    v2_agent = generate_agent_spec(v2_memo, version="v2")
    write_outputs(account_id, "v2", v2_memo, v2_agent, changelog)
    upsert_account_v2(v2_memo, v2_agent, changelog)
    print(f" ✓ v2 complete | {len(changelog['changes'])} fields updated")

if __name__ == "__main__":
    # Run all demo calls first
    for f in sorted(glob.glob("dataset/demo/*.txt")):
        run_pipeline_a(f)
    # Then all onboarding calls
    for f in sorted(glob.glob("dataset/onboarding/*.txt")):
        run_pipeline_b(f)
    print("\n✅ All 10 files processed successfully.")
