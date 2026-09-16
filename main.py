import os

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException

from classifier import classify_domain
from model import generate_coaching

load_dotenv()

app = FastAPI(
    title="FamilyGuard AI",
    version="1.0.0"
)

API_KEY = os.getenv("API_KEY")


def check_api_key(api_key):
    if not API_KEY or api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "familyguard-ai"
    }


@app.post("/classify")
def classify(
    data: dict,
    x_api_key: str = Header(None)
):
    check_api_key(x_api_key)

    domain = data.get("domain")

    if not domain:
        raise HTTPException(
            status_code=400,
            detail="domain is required"
        )

    risk = classify_domain(domain)

    return {
        "domain": domain,
        "risk": risk
    }


@app.post("/analyze")
def analyze(
    data: dict,
    x_api_key: str = Header(None)
):
    check_api_key(x_api_key)

    domain = data.get("domain")
    child_name = data.get("child_name")
    child_age = data.get("child_age")

    if not domain:
        raise HTTPException(
            status_code=400,
            detail="domain is required"
        )

    risk = classify_domain(domain)

    coaching = None

    if risk == "HIGH":
        coaching = generate_coaching(
            child_name=child_name,
            child_age=child_age,
            domain=domain
        )

    return {
        "domain": domain,
        "risk": risk,
        "coaching": coaching
    }