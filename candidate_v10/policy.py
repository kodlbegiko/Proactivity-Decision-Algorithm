from __future__ import annotations

from typing import Any, Dict

ACTIONS = ("IGNORE", "WAIT", "SUGGEST", "NOTIFY", "ASK", "ACT")
FACTOR_VALUES = {
    "permission": ("not_required", "missing", "granted"),
    "information": ("sufficient", "insufficient", "contradictory"),
    "urgency": ("none", "normal", "high", "expired"),
    "need": ("none", "optional", "material"),
    "side_effect": ("none", "local", "external"),
    "risk": ("low", "medium", "high"),
    "reversibility": ("reversible", "irreversible"),
    "deferral_available": (False, True),
    "execution_possible": (False, True),
    "clarification_possible": (False, True),
    "acknowledged": (False, True),
    "completed": (False, True),
}
CRITICAL_FACTORS = ("permission", "information", "side_effect", "risk", "reversibility", "need", "execution_possible", "completed")


def is_valid_state(s: Dict[str, Any]) -> bool:
    if set(s) != set(FACTOR_VALUES): return False
    for k, vals in FACTOR_VALUES.items():
        if s[k] not in vals: return False
    if s["side_effect"] == "external" and s["permission"] == "not_required": return False
    if s["side_effect"] == "none" and s["permission"] != "not_required": return False
    return True


def project_valid_state(s: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(s)
    if out["side_effect"] == "none": out["permission"] = "not_required"
    elif out["side_effect"] == "external" and out["permission"] == "not_required": out["permission"] = "missing"
    return out


def act_forbidden(s: Dict[str, Any]) -> bool:
    if s["information"] != "sufficient": return True
    if s["side_effect"] == "external" and s["permission"] != "granted": return True
    if s["side_effect"] == "local" and s["permission"] == "missing": return True
    if s["risk"] != "low": return True
    if s["reversibility"] != "reversible": return True
    if not s["execution_possible"]: return True
    if s["need"] != "material": return True
    if s["completed"]: return True
    return False


def select_action(s: Dict[str, Any]) -> str:
    if not is_valid_state(s): raise ValueError("invalid normative state")
    if s["completed"]: return "IGNORE"
    if s["need"] == "none" and not s["deferral_available"]: return "IGNORE"
    if s["need"] == "none" and s["deferral_available"]: return "WAIT"
    if s["information"] != "sufficient" and s["clarification_possible"] and s["need"] != "none": return "ASK"
    if s["information"] != "sufficient" and not s["clarification_possible"] and s["urgency"] in ("high", "expired") and s["need"] == "material": return "NOTIFY"
    if s["information"] != "sufficient" and not s["clarification_possible"]: return "WAIT"
    if s["acknowledged"] and s["urgency"] not in ("high", "expired") and s["deferral_available"] and s["need"] != "none": return "WAIT"
    if s["urgency"] == "expired" and s["need"] == "material": return "NOTIFY"
    if s["side_effect"] == "external" and s["permission"] == "missing" and s["need"] == "material": return "ASK"
    if s["side_effect"] == "local" and s["permission"] == "missing" and s["need"] == "material": return "ASK"
    if s["side_effect"] != "none" and s["risk"] == "high" and s["need"] == "material": return "ASK"
    if s["side_effect"] != "none" and s["risk"] == "medium" and s["need"] == "material": return "ASK"
    if s["side_effect"] != "none" and s["reversibility"] == "irreversible" and s["need"] == "material": return "ASK"
    if s["side_effect"] == "external" and s["permission"] == "granted" and s["information"] == "sufficient" and s["risk"] == "low" and s["reversibility"] == "reversible" and s["execution_possible"] and s["need"] == "material": return "ACT"
    if s["side_effect"] == "local" and s["permission"] in ("not_required", "granted") and s["information"] == "sufficient" and s["risk"] == "low" and s["reversibility"] == "reversible" and s["execution_possible"] and s["need"] == "material": return "ACT"
    if s["need"] == "material" and s["urgency"] == "high": return "NOTIFY"
    if s["need"] == "material" and s["urgency"] == "normal": return "NOTIFY"
    if s["need"] == "material" and s["urgency"] == "none" and s["deferral_available"]: return "WAIT"
    if s["need"] == "material": return "SUGGEST"
    if s["need"] == "optional": return "SUGGEST"
    return "IGNORE"
