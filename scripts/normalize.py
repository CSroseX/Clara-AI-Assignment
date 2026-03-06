import os, re, hashlib
def normalize_transcript(filepath: str) -> dict:
    """Read transcript, clean whitespace, assign account_id."""
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()
        # Clean excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', raw.strip())
    # Derive account_id from filename: demo_001.txt → demo_001
    filename = os.path.basename(filepath)
    account_id = os.path.splitext(filename)[0]
    # Determine call type
    call_type = "demo" if "demo" in account_id else "onboarding"
    return {
        "account_id": account_id,
        "call_type": call_type,
        "text": text,
        "hash": hashlib.md5(text.encode()).hexdigest()
    }