import json
from datetime import datetime, timezone

AGENT_PROMPT_TEMPLATE = open("prompts/agent_system_prompt.txt").read()

def generate_agent_spec(memo: dict, version: str = "v1") -> dict:
    """Fill prompt template with memo data → Retell Agent Spec."""
    bh = memo.get("business_hours", {})
    hours_str = (
        f"{', '.join(bh.get('days', []))} "
        f"{bh.get('start', 'TBD')} to {bh.get('end', 'TBD')}"
    ) if bh else "TBD"
    emergency_def = memo.get("emergency_definition", [])
    emergency_str = "; ".join(emergency_def) if emergency_def else "TBD"
    constraints = memo.get("integration_constraints", [])
    constraints_str = "; ".join(constraints) if constraints else "None specified"
    er = memo.get("emergency_routing_rules", {})
    filled_prompt = (AGENT_PROMPT_TEMPLATE
        .replace("{company_name}", memo.get("company_name", "our company"))
        .replace("{business_hours}", hours_str)
        .replace("{timezone}", bh.get("timezone", "local time"))
        .replace("{emergency_definition}", emergency_str)
        .replace("{emergency_line}", er.get("primary_phone", "TBD"))
        .replace("{integration_constraints}", constraints_str)
    )
    return {
        "agent_name": f"Clara - {memo.get('company_name', 'Unknown')}",
        "version": version,
        "account_id": memo.get("account_id"),
        "voice_style": "professional_female",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "key_variables": {
            "company_name": memo.get("company_name"),
            "timezone": bh.get("timezone"),
            "business_hours": hours_str,
            "office_address": str(memo.get("office_address", {})),
            "emergency_line": er.get("primary_phone"),
            "fallback_line": er.get("fallback_phone"),
        },
        "tool_placeholders": ["transfer_call", "send_sms_followup", "log_call_record"],
        "call_transfer_protocol": {
            "timeout_seconds": memo.get("call_transfer_rules", {}).get("timeout_seconds", 60),
            "fail_action": "apologize_and_assure_callback"
        },
        "fallback_protocol": {
            "message": memo.get("call_transfer_rules", {}).get("fail_message",
                "I apologize, our team is unavailable. Someone will call you back shortly."),
            "collect_callback_number": True
        },
        "system_prompt": filled_prompt
    }