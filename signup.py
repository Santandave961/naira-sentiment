"""
signup.py

One-command helper to sign up for a Naira Sentiment API key, instead of
manually clicking through the /docs Swagger UI each time.

NOTE: the exact SignupRequest field names weren't confirmed from /docs
(only POST /analyze's schema was verified). This assumes {"email": ...}
based on the field being visible but collapsed in the docs screenshot —
expand the "SignupRequest" schema at /docs to confirm the real field
names before relying on this, and adjust the payload below if needed.

Usage:
    python signup.py --email you@example.com
"""

import argparse
import json
import requests

BASE_URL = "https://naira-sentiment-api-1.onrender.com"
SIGNUP_ENDPOINT = f"{BASE_URL}/signup"


def signup(email: str) -> dict:
    print(f"Signing up with {SIGNUP_ENDPOINT} ...")
    print("(Free-tier hosting — first request may take a few seconds to wake up.)")

    response = requests.post(
        SIGNUP_ENDPOINT,
        json={"email": email},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(description="Sign up for a Naira Sentiment API key.")
    parser.add_argument("--email", required=True, help="Email address to sign up with")
    args = parser.parse_args()

    try:
        result = signup(args.email)
    except requests.HTTPError as e:
        print(f"Signup failed: {e}")
        print(f"Response body: {e.response.text}")
        return
    except Exception as e:
        print(f"Signup failed: {e}")
        return

    print("\nSignup response:")
    print(json.dumps(result, indent=2))
    print(
        "\nIf an API key is included above, set it as an environment "
        "variable before running the pipeline:\n"
        "  export NAIRA_API_KEY=<your key>"
    )


if __name__ == "__main__":
    main()