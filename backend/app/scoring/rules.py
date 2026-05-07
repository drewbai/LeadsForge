def apply_rules(lead: dict) -> int:
    score = 0
    email_domain = lead.get("email_domain")
    if email_domain:
        score += 10

    quality = lead.get("email_quality")
    if quality == "alias":
        score += 5
    elif quality == "free_provider":
        score += 3

    return score
