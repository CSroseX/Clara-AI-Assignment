import os, json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
EXTRACTION_PROMPT = open("prompts/extraction_prompt.txt").read()
def extract_account_memo(transcript: dict) -> dict:
    """Send transcript to Groq, return parsed Account Memo JSON."""
    prompt = EXTRACTION_PROMPT.replace("{transcript}", transcript["text"])
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,  # Critical: prevents hallucination in extraction
        max_tokens=2000
    )
    raw = response.choices[0].message.content.strip()
    # Strip markdown fences if model adds them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
    if raw.startswith("json"):
        raw = raw[4:]
    try:
        memo = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON: {e}\nRaw: {raw}") from e
    
    # Enforce schema completeness: questions_or_unknowns must be a list, even if empty
    if "questions_or_unknowns" in memo:
        if not isinstance(memo["questions_or_unknowns"], list):
            raise ValueError(f"questions_or_unknowns must be a list, got {type(memo['questions_or_unknowns'])}")
    else:
        # Null fields acceptable; missing keys get default empty list
        memo["questions_or_unknowns"] = []
    
    # Inject metadata
    memo["account_id"] = transcript["account_id"]
    memo["version"] = "v1"
    memo["source"] = transcript["call_type"] + "_call"
    return memo