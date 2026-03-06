"""
run_single.py — Entry point called by n8n for each transcript file.

Usage:
  python scripts/run_single.py --file dataset/demo/demo_001.txt --pipeline a
  python scripts/run_single.py --file dataset/onboarding/onboarding_001.txt --pipeline b --account-id demo_001

n8n parses stdout for these markers:
  account_id: <value>
  company: <value>
  issue_url: <url>
  changes_count: <number>
"""

import argparse
import json
import os
import sys
import traceback
from datetime import datetime, timezone

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))

from normalize import normalize_transcript
from extract import extract_account_memo
from prompt_generator import generate_agent_spec
from patch import apply_patch
from supabase_client import upsert_account_v1, upsert_account_v2
from github_tracker import create_account_issue
from output_writer import write_outputs


def run_pipeline_a(filepath: str):
    """Demo call → v1 memo + agent spec. Called by n8n Pipeline A workflow."""
    print(f"[Pipeline A] Starting: {filepath}", flush=True)

    transcript = normalize_transcript(filepath)
    memo = extract_account_memo(transcript)
    agent = generate_agent_spec(memo, version="v1")

    write_outputs(memo["account_id"], "v1", memo, agent)
    upsert_account_v1(memo, agent)
    issue_url = create_account_issue(
        memo["account_id"],
        memo.get("company_name", "Unknown"),
        "v1"
    )

    # Print markers for n8n Parse Result node to extract
    print(f"account_id: {memo['account_id']}", flush=True)
    print(f"company: {memo.get('company_name', 'Unknown')}", flush=True)
    print(f"issue_url: {issue_url or 'none'}", flush=True)
    print(f"[Pipeline A] Complete: {memo['account_id']}", flush=True)


def run_pipeline_b(filepath: str, account_id: str):
    """Onboarding call → v2 patch + changelog. Called by n8n Pipeline B workflow."""
    print(f"[Pipeline B] Starting: {filepath} → {account_id}", flush=True)

    # Load existing v1 memo
    v1_path = f"outputs/accounts/{account_id}/v1/account_memo.json"
    if not os.path.exists(v1_path):
        print(f"ERROR: v1 memo not found at {v1_path}", flush=True)
        sys.exit(1)

    with open(v1_path) as f:
        v1_memo = json.load(f)

    # Extract updates from onboarding transcript
    transcript = normalize_transcript(filepath)
    updates = extract_account_memo(transcript)

    # Patch v1 → v2
    v2_memo, changelog = apply_patch(v1_memo, updates)
    v2_agent = generate_agent_spec(v2_memo, version="v2")

    # Write outputs and update storage
    write_outputs(account_id, "v2", v2_memo, v2_agent, changelog)
    upsert_account_v2(v2_memo, v2_agent, changelog)

    changes_count = len(changelog.get("changes", []))

    # Print markers for n8n Parse v2 Result node
    print(f"account_id: {account_id}", flush=True)
    print(f"changes_count: {changes_count}", flush=True)
    print(f"[Pipeline B] Complete: {account_id} | {changes_count} fields updated", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Clara Pipeline entry point for n8n")
    parser.add_argument("--file", required=True, help="Path to transcript file")
    parser.add_argument("--pipeline", required=True, choices=["a", "b"], help="Which pipeline to run")
    parser.add_argument("--account-id", help="Account ID override for Pipeline B (derived from filename if not set)")
    args = parser.parse_args()

    try:
        if args.pipeline == "a":
            run_pipeline_a(args.file)
        elif args.pipeline == "b":
            # Derive account_id from filename if not explicitly passed
            account_id = args.account_id
            if not account_id:
                filename = os.path.basename(args.file).replace(".txt", "")
                account_id = filename.replace("onboarding_", "demo_")
            run_pipeline_b(args.file, account_id)

    except Exception as e:
        print(f"FATAL ERROR: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()