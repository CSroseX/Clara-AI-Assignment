import os, json
from supabase import create_client
from dotenv import load_dotenv
load_dotenv()
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
def upsert_account_v1(memo: dict, agent_spec: dict):
 """Insert or update account with v1 data."""
 sb.table("accounts").upsert({
 "account_id": memo["account_id"],
 "company_name": memo.get("company_name"),
 "memo_v1": memo,
 "agent_spec_v1": agent_spec,
 "status": "demo_processed",
 "current_version": "v1"
 }).execute()
def upsert_account_v2(memo_v2: dict, agent_spec_v2: dict, changelog: dict):
 """Update account with v2 data and log changelog."""
 sb.table("accounts").update({
 "memo_v2": memo_v2,
 "agent_spec_v2": agent_spec_v2,
 "status": "onboarding_complete",
 "current_version": "v2"
 }).eq("account_id", memo_v2["account_id"]).execute()
 sb.table("changelog").insert({
 "account_id": memo_v2["account_id"],
 "from_version": "v1",
 "to_version": "v2",
 "changes": changelog,
 "source": "onboarding_call"
 }).execute()
