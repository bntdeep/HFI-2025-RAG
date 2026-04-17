"""
HFI country registry: all 165 jurisdictions covered by the 2025 Human Freedom Index.
Flag emojis are derived from ISO 3166-1 alpha-2 codes via regional indicator symbols.
"""


def _flag(iso2: str) -> str:
    """Convert 2-letter ISO code to flag emoji."""
    return "".join(chr(ord(c) - ord("A") + 0x1F1E6) for c in iso2.upper())


# (name, iso2_code, region)
_RAW: list[tuple[str, str, str]] = [
    # Africa
    ("Algeria", "DZ", "Africa"),
    ("Angola", "AO", "Africa"),
    ("Benin", "BJ", "Africa"),
    ("Botswana", "BW", "Africa"),
    ("Burkina Faso", "BF", "Africa"),
    ("Burundi", "BI", "Africa"),
    ("Cabo Verde", "CV", "Africa"),
    ("Cameroon", "CM", "Africa"),
    ("Central African Republic", "CF", "Africa"),
    ("Chad", "TD", "Africa"),
    ("Comoros", "KM", "Africa"),
    ("Congo", "CG", "Africa"),
    ("Côte d'Ivoire", "CI", "Africa"),
    ("Democratic Republic of the Congo", "CD", "Africa"),
    ("Egypt", "EG", "Africa"),
    ("Eswatini", "SZ", "Africa"),
    ("Ethiopia", "ET", "Africa"),
    ("Gabon", "GA", "Africa"),
    ("Gambia", "GM", "Africa"),
    ("Ghana", "GH", "Africa"),
    ("Guinea", "GN", "Africa"),
    ("Guinea-Bissau", "GW", "Africa"),
    ("Kenya", "KE", "Africa"),
    ("Lesotho", "LS", "Africa"),
    ("Liberia", "LR", "Africa"),
    ("Libya", "LY", "Africa"),
    ("Madagascar", "MG", "Africa"),
    ("Malawi", "MW", "Africa"),
    ("Mali", "ML", "Africa"),
    ("Mauritania", "MR", "Africa"),
    ("Mauritius", "MU", "Africa"),
    ("Morocco", "MA", "Africa"),
    ("Mozambique", "MZ", "Africa"),
    ("Namibia", "NA", "Africa"),
    ("Niger", "NE", "Africa"),
    ("Nigeria", "NG", "Africa"),
    ("Rwanda", "RW", "Africa"),
    ("São Tomé and Príncipe", "ST", "Africa"),
    ("Senegal", "SN", "Africa"),
    ("Sierra Leone", "SL", "Africa"),
    ("South Africa", "ZA", "Africa"),
    ("Sudan", "SD", "Africa"),
    ("Tanzania", "TZ", "Africa"),
    ("Togo", "TG", "Africa"),
    ("Tunisia", "TN", "Africa"),
    ("Uganda", "UG", "Africa"),
    ("Zambia", "ZM", "Africa"),
    ("Zimbabwe", "ZW", "Africa"),
    # Americas
    ("Argentina", "AR", "Americas"),
    ("Bahamas", "BS", "Americas"),
    ("Barbados", "BB", "Americas"),
    ("Belize", "BZ", "Americas"),
    ("Bolivia", "BO", "Americas"),
    ("Brazil", "BR", "Americas"),
    ("Canada", "CA", "Americas"),
    ("Chile", "CL", "Americas"),
    ("Colombia", "CO", "Americas"),
    ("Costa Rica", "CR", "Americas"),
    ("Dominican Republic", "DO", "Americas"),
    ("Ecuador", "EC", "Americas"),
    ("El Salvador", "SV", "Americas"),
    ("Guatemala", "GT", "Americas"),
    ("Guyana", "GY", "Americas"),
    ("Haiti", "HT", "Americas"),
    ("Honduras", "HN", "Americas"),
    ("Jamaica", "JM", "Americas"),
    ("Mexico", "MX", "Americas"),
    ("Nicaragua", "NI", "Americas"),
    ("Panama", "PA", "Americas"),
    ("Paraguay", "PY", "Americas"),
    ("Peru", "PE", "Americas"),
    ("Trinidad and Tobago", "TT", "Americas"),
    ("United States", "US", "Americas"),
    ("Uruguay", "UY", "Americas"),
    ("Venezuela", "VE", "Americas"),
    # Asia-Pacific
    ("Australia", "AU", "Asia-Pacific"),
    ("Bangladesh", "BD", "Asia-Pacific"),
    ("Cambodia", "KH", "Asia-Pacific"),
    ("China", "CN", "Asia-Pacific"),
    ("Fiji", "FJ", "Asia-Pacific"),
    ("India", "IN", "Asia-Pacific"),
    ("Indonesia", "ID", "Asia-Pacific"),
    ("Japan", "JP", "Asia-Pacific"),
    ("Laos", "LA", "Asia-Pacific"),
    ("Malaysia", "MY", "Asia-Pacific"),
    ("Mongolia", "MN", "Asia-Pacific"),
    ("Myanmar", "MM", "Asia-Pacific"),
    ("Nepal", "NP", "Asia-Pacific"),
    ("New Zealand", "NZ", "Asia-Pacific"),
    ("Pakistan", "PK", "Asia-Pacific"),
    ("Papua New Guinea", "PG", "Asia-Pacific"),
    ("Philippines", "PH", "Asia-Pacific"),
    ("Singapore", "SG", "Asia-Pacific"),
    ("Solomon Islands", "SB", "Asia-Pacific"),
    ("South Korea", "KR", "Asia-Pacific"),
    ("Sri Lanka", "LK", "Asia-Pacific"),
    ("Taiwan", "TW", "Asia-Pacific"),
    ("Thailand", "TH", "Asia-Pacific"),
    ("Timor-Leste", "TL", "Asia-Pacific"),
    ("Vietnam", "VN", "Asia-Pacific"),
    # Europe
    ("Albania", "AL", "Europe"),
    ("Armenia", "AM", "Europe"),
    ("Austria", "AT", "Europe"),
    ("Azerbaijan", "AZ", "Europe"),
    ("Belarus", "BY", "Europe"),
    ("Belgium", "BE", "Europe"),
    ("Bosnia and Herzegovina", "BA", "Europe"),
    ("Bulgaria", "BG", "Europe"),
    ("Croatia", "HR", "Europe"),
    ("Cyprus", "CY", "Europe"),
    ("Czech Republic", "CZ", "Europe"),
    ("Denmark", "DK", "Europe"),
    ("Estonia", "EE", "Europe"),
    ("Finland", "FI", "Europe"),
    ("France", "FR", "Europe"),
    ("Georgia", "GE", "Europe"),
    ("Germany", "DE", "Europe"),
    ("Greece", "GR", "Europe"),
    ("Hungary", "HU", "Europe"),
    ("Iceland", "IS", "Europe"),
    ("Ireland", "IE", "Europe"),
    ("Israel", "IL", "Europe"),
    ("Italy", "IT", "Europe"),
    ("Kazakhstan", "KZ", "Europe"),
    ("Kyrgyzstan", "KG", "Europe"),
    ("Latvia", "LV", "Europe"),
    ("Lithuania", "LT", "Europe"),
    ("Luxembourg", "LU", "Europe"),
    ("Malta", "MT", "Europe"),
    ("Moldova", "MD", "Europe"),
    ("Montenegro", "ME", "Europe"),
    ("Netherlands", "NL", "Europe"),
    ("North Macedonia", "MK", "Europe"),
    ("Norway", "NO", "Europe"),
    ("Poland", "PL", "Europe"),
    ("Portugal", "PT", "Europe"),
    ("Romania", "RO", "Europe"),
    ("Russia", "RU", "Europe"),
    ("Slovakia", "SK", "Europe"),
    ("Slovenia", "SI", "Europe"),
    ("Spain", "ES", "Europe"),
    ("Sweden", "SE", "Europe"),
    ("Switzerland", "CH", "Europe"),
    ("Tajikistan", "TJ", "Europe"),
    ("Turkey", "TR", "Europe"),
    ("Turkmenistan", "TM", "Europe"),
    ("Ukraine", "UA", "Europe"),
    ("United Kingdom", "GB", "Europe"),
    ("Uzbekistan", "UZ", "Europe"),
    # Middle East & North Africa
    ("Bahrain", "BH", "Middle East & North Africa"),
    ("Iran", "IR", "Middle East & North Africa"),
    ("Iraq", "IQ", "Middle East & North Africa"),
    ("Jordan", "JO", "Middle East & North Africa"),
    ("Kuwait", "KW", "Middle East & North Africa"),
    ("Lebanon", "LB", "Middle East & North Africa"),
    ("Oman", "OM", "Middle East & North Africa"),
    ("Qatar", "QA", "Middle East & North Africa"),
    ("Saudi Arabia", "SA", "Middle East & North Africa"),
    ("United Arab Emirates", "AE", "Middle East & North Africa"),
    ("Yemen", "YE", "Middle East & North Africa"),
]

# Build the main registry
COUNTRIES: list[dict] = [
    {
        "name": name,
        "iso2": iso2,
        "flag": _flag(iso2),
        "region": region,
    }
    for name, iso2, region in _RAW
]

# Fast lookups
_BY_NAME: dict[str, dict] = {c["name"].lower(): c for c in COUNTRIES}
_BY_ISO2: dict[str, dict] = {c["iso2"].upper(): c for c in COUNTRIES}

# Alternate name aliases (common variations found in the HFI PDF)
ALIASES: dict[str, str] = {
    "usa": "United States",
    "u.s.": "United States",
    "u.s.a.": "United States",
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
    "great britain": "United Kingdom",
    "england": "United Kingdom",
    "czechia": "Czech Republic",
    "drc": "Democratic Republic of the Congo",
    "dr congo": "Democratic Republic of the Congo",
    "congo, dem. rep.": "Democratic Republic of the Congo",
    "congo, rep.": "Congo",
    "republic of korea": "South Korea",
    "korea, rep.": "South Korea",
    "korea, south": "South Korea",
    "russia": "Russia",
    "russian federation": "Russia",
    "türkiye": "Turkey",
    "lao pdr": "Laos",
    "lao": "Laos",
    "ivory coast": "Côte d'Ivoire",
    "cote d'ivoire": "Côte d'Ivoire",
    "swaziland": "Eswatini",
    "burma": "Myanmar",
    "taiwan, china": "Taiwan",
    "chinese taipei": "Taiwan",
    "timor leste": "Timor-Leste",
    "east timor": "Timor-Leste",
    "sao tome and principe": "São Tomé and Príncipe",
    "trinidad & tobago": "Trinidad and Tobago",
    "bosnia": "Bosnia and Herzegovina",
    "bosnia-herzegovina": "Bosnia and Herzegovina",
    "north macedonia": "North Macedonia",
    "republic of north macedonia": "North Macedonia",
    "macedonia": "North Macedonia",
    "cabo verde": "Cabo Verde",
    "cape verde": "Cabo Verde",
}


def get_country(name: str) -> dict | None:
    """Look up a country by name or alias (case-insensitive)."""
    key = name.strip().lower()
    if key in _BY_NAME:
        return _BY_NAME[key]
    canonical = ALIASES.get(key)
    if canonical:
        return _BY_NAME.get(canonical.lower())
    return None


def get_country_by_iso2(iso2: str) -> dict | None:
    return _BY_ISO2.get(iso2.upper())


def get_flag(country_name: str) -> str:
    c = get_country(country_name)
    return c["flag"] if c else "🏳"


COUNTRY_NAMES: list[str] = [c["name"] for c in COUNTRIES]
