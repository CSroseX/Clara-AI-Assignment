# Clara Answers — Automation Pipeline
## What This Does
Converts demo + onboarding call transcripts into:
- Structured Account Memo JSON (v1 from demo, v2 from onboarding)
- Retell Agent Spec JSON (ready to import)
- Versioned outputs with changelogs
- Supabase persistence + GitHub issue tracking
## Architecture
transcript → normalize → Groq LLM extract → memo JSON → agent spec → Supabase + files
onboarding → extract updates → patch v1 → v2 memo → v2 agent → changelog
## Quick Start
### 1. Prerequisites
- Python 3.11+
- Docker (for n8n)
- Free accounts: Groq, Supabase, GitHub
### 2. Install
git clone https://github.com/your-username/clara-pipeline
cd clara-pipeline
pip install -r requirements.txt
cp .env.example .env # Fill in your keys
### 3. Set Up Database
# Paste SQL from /scripts/create_tables.sql into Supabase SQL Editor
### 4. Start n8n
docker-compose up -d
# Open http://localhost:5678
# Import workflows/pipeline_a_demo.json and pipeline_b_onboarding.json
### 5. Add Dataset
# Copy demo transcripts to dataset/demo/
# Copy onboarding transcripts to dataset/onboarding/
### 6. Run
python scripts/batch_run.py
### 7. View Outputs
outputs/accounts/<account_id>/v1/account_memo.json
outputs/accounts/<account_id>/v1/agent_spec.json
outputs/accounts/<account_id>/v2/account_memo.json
outputs/accounts/<account_id>/v2/agent_spec.json
outputs/accounts/<account_id>/v2/changelog.json
## Environment Variables
GROQ_API_KEY= # From console.groq.com
SUPABASE_URL= # From Supabase Settings → API
SUPABASE_KEY= # Supabase anon key
GITHUB_TOKEN= # GitHub personal access token
GITHUB_REPO= # your-username/clara-pipeline
## Known Limitations
- Retell agent creation is via spec JSON only (manual import if API not free)
- Audio transcription requires local Whisper install (transcripts = primary input)
- GitHub Issues used instead of Asana (both satisfy tracking requirement)
## What I Would Improve With Production Access
- Retell API integration for programmatic agent creation
- Webhook-triggered ingestion instead of file watch
- Vector similarity search for duplicate account detection
- Dashboard UI for reviewing extraction quality per account