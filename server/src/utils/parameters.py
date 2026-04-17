"""
HFI parameter definitions — codes, display names, and aliases.
Based on the 2025 Human Freedom Index methodology.
"""
from dataclasses import dataclass, field


@dataclass
class Parameter:
    code: str          # e.g. "pf_rol"
    name: str          # display name
    parent: str | None # parent category code
    aliases: list[str] = field(default_factory=list)


HFI_PARAMETERS: list[Parameter] = [
    # ── Top-level scores ─────────────────────────────────────────────────────
    Parameter("hf",  "Human Freedom",    None,
              aliases=["human freedom index", "hfi", "overall score", "overall freedom"]),
    Parameter("pf",  "Personal Freedom", None,
              aliases=["personal freedom score"]),
    Parameter("ef",  "Economic Freedom", None,
              aliases=["economic freedom score", "economic freedom of the world", "efw"]),

    # ── Personal Freedom ─────────────────────────────────────────────────────
    Parameter("pf_rol", "Rule of Law", "pf",
              aliases=["rule of law", "legal system", "judicial"]),
    Parameter("pf_rol_procedural",  "Procedural Justice",        "pf_rol",
              aliases=["procedural justice"]),
    Parameter("pf_rol_civil",       "Civil Justice",             "pf_rol",
              aliases=["civil justice"]),
    Parameter("pf_rol_criminal",    "Criminal Justice",          "pf_rol",
              aliases=["criminal justice"]),

    Parameter("pf_ss", "Security and Safety", "pf",
              aliases=["security", "safety", "personal security"]),
    Parameter("pf_ss_homicide",       "Homicide",                    "pf_ss",
              aliases=["homicide rate", "murder rate"]),
    Parameter("pf_ss_disappearances", "Disappearances and Conflict",  "pf_ss",
              aliases=["disappearances", "conflict", "terrorism"]),
    Parameter("pf_ss_women",          "Women's Security",             "pf_ss",
              aliases=["women security", "women's safety"]),

    Parameter("pf_movement", "Freedom of Movement", "pf",
              aliases=["movement", "freedom of movement", "mobility"]),
    Parameter("pf_movement_domestic", "Domestic Movement",         "pf_movement",
              aliases=["domestic movement"]),
    Parameter("pf_movement_foreign",  "Foreign Movement",          "pf_movement",
              aliases=["foreign movement", "freedom to travel"]),
    Parameter("pf_movement_women",    "Women's Freedom of Movement", "pf_movement",
              aliases=["women movement", "women's movement"]),

    Parameter("pf_religion", "Freedom of Religion", "pf",
              aliases=["religion", "religious freedom", "religious liberty"]),
    Parameter("pf_religion_freedom",    "Religious Freedom",     "pf_religion"),
    Parameter("pf_religion_harassment", "Religious Harassment",  "pf_religion"),

    Parameter("pf_association", "Freedom of Association", "pf",
              aliases=["association", "assembly", "civil society", "freedom of assembly"]),
    Parameter("pf_assembly",          "Freedom of Assembly",                   "pf_association",
              aliases=["freedom of assembly"]),
    Parameter("pf_assembly_cso",      "Civil Society Organizations",           "pf_association",
              aliases=["cso", "civil society organizations"]),
    Parameter("pf_assembly_parties",  "Political Parties",                     "pf_association",
              aliases=["political parties"]),

    Parameter("pf_expression", "Freedom of Expression", "pf",
              aliases=["expression", "press freedom", "freedom of speech", "free speech",
                       "freedom of the press", "media freedom"]),
    Parameter("pf_expression_press",    "Press Freedom",         "pf_expression",
              aliases=["press freedom", "freedom of the press", "media"]),
    Parameter("pf_expression_internet", "Internet Freedom",      "pf_expression",
              aliases=["internet", "internet freedom", "cable"]),
    Parameter("pf_expression_political","Political Expression",  "pf_expression",
              aliases=["political expression"]),

    Parameter("pf_identity", "Identity and Relationships", "pf",
              aliases=["identity", "relationships", "lgbtq", "same-sex", "gender identity"]),
    Parameter("pf_identity_legal",    "Legal Gender Identity",    "pf_identity",
              aliases=["gender identity", "legal gender"]),
    Parameter("pf_identity_same_sex", "Same-Sex Relationships",   "pf_identity",
              aliases=["same-sex", "homosexuality", "lgbt", "lgbtq"]),
    Parameter("pf_identity_divorce",  "Divorce Rights",           "pf_identity",
              aliases=["divorce"]),

    # ── Economic Freedom ─────────────────────────────────────────────────────
    Parameter("ef_government", "Size of Government", "ef",
              aliases=["government size", "size of government", "government spending",
                       "fiscal policy"]),
    Parameter("ef_government_spending",    "Government Spending",          "ef_government",
              aliases=["government spending", "public spending"]),
    Parameter("ef_government_transfers",   "Transfers and Subsidies",      "ef_government",
              aliases=["transfers", "subsidies"]),
    Parameter("ef_government_enterprises", "Government Enterprises",       "ef_government",
              aliases=["state enterprises", "soe"]),
    Parameter("ef_government_top_rates",   "Top Marginal Tax Rate",        "ef_government",
              aliases=["top tax rate", "marginal tax rate", "tax rate"]),

    Parameter("ef_legal", "Legal System and Property Rights", "ef",
              aliases=["legal system", "property rights", "rule of law", "judicial independence"]),
    Parameter("ef_legal_judicial",    "Judicial Independence",     "ef_legal",
              aliases=["judicial independence"]),
    Parameter("ef_legal_courts",      "Impartial Courts",          "ef_legal",
              aliases=["impartial courts"]),
    Parameter("ef_legal_property",    "Property Rights",           "ef_legal",
              aliases=["property rights"]),
    Parameter("ef_legal_military",    "Military Interference",     "ef_legal",
              aliases=["military interference"]),
    Parameter("ef_legal_integrity",   "Integrity of Legal System", "ef_legal"),
    Parameter("ef_legal_enforcement", "Legal Enforcement",         "ef_legal"),
    Parameter("ef_legal_police",      "Reliability of Police",     "ef_legal",
              aliases=["police reliability"]),
    Parameter("ef_legal_crime",       "Business Cost of Crime",    "ef_legal",
              aliases=["crime cost", "cost of crime"]),

    Parameter("ef_money", "Sound Money", "ef",
              aliases=["sound money", "monetary freedom", "inflation", "money supply"]),
    Parameter("ef_money_growth",    "Money Growth",           "ef_money",
              aliases=["money growth", "monetary growth"]),
    Parameter("ef_money_sd",        "Standard Deviation of Inflation", "ef_money"),
    Parameter("ef_money_inflation", "Inflation",              "ef_money",
              aliases=["inflation rate"]),
    Parameter("ef_money_currency",  "Freedom to Hold Foreign Currency", "ef_money",
              aliases=["foreign currency", "currency freedom"]),

    Parameter("ef_trade", "Freedom to Trade Internationally", "ef",
              aliases=["trade freedom", "free trade", "international trade",
                       "tariffs", "trade barriers"]),
    Parameter("ef_trade_tariffs",       "Tariffs",                  "ef_trade",
              aliases=["tariff", "tariff rate"]),
    Parameter("ef_trade_regulatory",    "Regulatory Trade Barriers","ef_trade",
              aliases=["non-tariff barriers", "regulatory barriers"]),
    Parameter("ef_trade_black_market",  "Black-Market Exchange",    "ef_trade",
              aliases=["black market", "parallel exchange"]),
    Parameter("ef_trade_controls",      "Capital Controls",         "ef_trade",
              aliases=["capital controls", "capital movements"]),

    Parameter("ef_regulation", "Regulation", "ef",
              aliases=["regulation", "business regulation", "labour regulation"]),
    Parameter("ef_regulation_credit",   "Credit Market Regulations", "ef_regulation",
              aliases=["credit regulation", "financial regulation"]),
    Parameter("ef_regulation_labor",    "Labor Market Regulations",  "ef_regulation",
              aliases=["labour regulation", "labor regulation", "employment regulation",
                       "minimum wage", "hiring and firing"]),
    Parameter("ef_regulation_business", "Business Regulations",      "ef_regulation",
              aliases=["business regulation", "ease of doing business"]),
]

# Fast lookup structures
_BY_CODE: dict[str, Parameter] = {p.code: p for p in HFI_PARAMETERS}
_BY_NAME_LOWER: dict[str, Parameter] = {p.name.lower(): p for p in HFI_PARAMETERS}

# Build alias map: alias_lower → canonical code
_ALIAS_MAP: dict[str, str] = {}
for _p in HFI_PARAMETERS:
    for _alias in _p.aliases:
        _ALIAS_MAP[_alias.lower()] = _p.code


def get_parameter(code_or_name: str) -> Parameter | None:
    key = code_or_name.strip().lower()
    if key in _BY_CODE:
        return _BY_CODE[key]
    if key in _BY_NAME_LOWER:
        return _BY_NAME_LOWER[key]
    canonical_code = _ALIAS_MAP.get(key)
    if canonical_code:
        return _BY_CODE.get(canonical_code)
    return None


def get_children(parent_code: str) -> list[Parameter]:
    return [p for p in HFI_PARAMETERS if p.parent == parent_code]


PARAMETER_CODES: list[str] = [p.code for p in HFI_PARAMETERS]
PARAMETER_NAMES: list[str] = [p.name for p in HFI_PARAMETERS]
