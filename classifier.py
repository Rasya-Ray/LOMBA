ADULT_KEYWORDS = [
    "porn",
    "xxx",
    "adult",
    "sex"
]

GAMBLING_KEYWORDS = [
    "casino",
    "bet",
    "poker",
    "slot"
]


def classify_domain(domain):
    domain = domain.lower()

    for keyword in ADULT_KEYWORDS:
        if keyword in domain:
            return "HIGH"

    for keyword in GAMBLING_KEYWORDS:
        if keyword in domain:
            return "HIGH"

    return "LOW"