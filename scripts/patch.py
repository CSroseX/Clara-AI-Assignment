import json
from deepdiff import DeepDiff
from datetime import datetime, timezone

def apply_patch(v1_memo: dict, onboarding_updates: dict) -> tuple[dict, dict]:
    """Merge onboarding updates into v1 memo. Return (v2_memo, changelog)."""
    v2 = v1_memo.copy()
    
    def deep_update(base: dict, updates: dict):
        """Recursively update base with non-null values from updates."""
        for key, val in updates.items():
            if val is None:
                continue  # Never overwrite with null
            if isinstance(val, dict) and isinstance(base.get(key), dict):
                deep_update(base[key], val)
            else:
                base[key] = val
    
    deep_update(v2, onboarding_updates)
    v2["version"] = "v2"
    v2["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Generate human-readable changelog
    diff = DeepDiff(v1_memo, v2, ignore_order=True)
    changes = []
    for change_type, items in diff.items():
        for path, detail in (items.items() if isinstance(items, dict) else enumerate(items)):
            if isinstance(detail, dict):
                changes.append({
                    "field": path,
                    "old": detail.get("old_value"),
                    "new": detail.get("new_value"),
                    "reason": "Updated during onboarding call"
                })
    
    changelog = {
        "account_id": v2["account_id"],
        "from_version": "v1",
        "to_version": "v2",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "onboarding_call",
        "changes": changes
    }
    return v2, changelog