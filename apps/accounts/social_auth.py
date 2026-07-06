"""
Server-side verification of Google / Facebook OAuth access tokens.

The frontend obtains an OAuth *access token* from the provider's JS SDK and
sends it to /api/accounts/social-user/. We must NEVER trust a client-supplied
email: we verify the token directly with the provider, confirm it was issued
for *our* app, and read the verified email from the provider's response.

Requires `requests` (already used elsewhere in the project) and these settings:
    GOOGLE_OAUTH_CLIENT_ID   # must equal the frontend NEXT_PUBLIC_GOOGLE_CLIENT_ID
    FACEBOOK_APP_ID
    FACEBOOK_APP_SECRET
"""

import requests
from django.conf import settings

# Google
GOOGLE_TOKENINFO = "https://oauth2.googleapis.com/tokeninfo"
GOOGLE_USERINFO = "https://www.googleapis.com/oauth2/v3/userinfo"
# Facebook
FB_DEBUG_TOKEN = "https://graph.facebook.com/debug_token"
FB_ME = "https://graph.facebook.com/me"

TIMEOUT = 10  # seconds


class SocialAuthError(Exception):
    """Raised when a social token cannot be verified. Message is user-safe."""


def _get(url, **params):
    try:
        return requests.get(url, params=params or None, timeout=TIMEOUT)
    except requests.RequestException as exc:
        raise SocialAuthError("Could not reach the identity provider. Try again.") from exc


def _truthy(value):
    return str(value).lower() in ("true", "1")


def verify_google(access_token):
    """Validate a Google access token and return {email, first_name, last_name}."""
    # 1) tokeninfo validates the token and exposes its audience + verified email.
    resp = _get(GOOGLE_TOKENINFO, access_token=access_token)
    if resp.status_code != 200:
        raise SocialAuthError("Invalid or expired Google token.")
    info = resp.json()

    client_id = getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", None)
    audience = info.get("aud") or info.get("azp")
    if client_id and audience != client_id:
        raise SocialAuthError("Google token was not issued for this application.")

    email = info.get("email")
    if not email or not _truthy(info.get("email_verified", "false")):
        raise SocialAuthError("Google account has no verified email address.")

    # 2) userinfo (best-effort) fills in the display name.
    first = last = ""
    try:
        ur = requests.get(
            GOOGLE_USERINFO,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=TIMEOUT,
        )
        if ur.status_code == 200:
            data = ur.json()
            first = data.get("given_name", "") or ""
            last = data.get("family_name", "") or ""
    except requests.RequestException:
        pass

    return {"email": email.lower(), "first_name": first, "last_name": last}


def verify_facebook(access_token):
    """Validate a Facebook access token and return {email, first_name, last_name}."""
    app_id = getattr(settings, "FACEBOOK_APP_ID", None)
    app_secret = getattr(settings, "FACEBOOK_APP_SECRET", None)
    if not app_id or not app_secret:
        raise SocialAuthError("Facebook login is not configured on the server.")

    # 1) debug_token confirms the token is valid AND belongs to our app.
    app_token = f"{app_id}|{app_secret}"
    dr = _get(FB_DEBUG_TOKEN, input_token=access_token, access_token=app_token)
    if dr.status_code != 200:
        raise SocialAuthError("Invalid Facebook token.")
    data = dr.json().get("data", {})
    if not data.get("is_valid") or str(data.get("app_id")) != str(app_id):
        raise SocialAuthError("Facebook token was not issued for this application.")

    # 2) Read the profile. email requires the approved `email` permission.
    mr = _get(FB_ME, fields="id,first_name,last_name,email", access_token=access_token)
    if mr.status_code != 200:
        raise SocialAuthError("Could not fetch your Facebook profile.")
    me = mr.json()

    email = me.get("email")
    if not email:
        raise SocialAuthError(
            "Your Facebook account didn't share an email address. "
            "Please sign in with Google or email instead."
        )

    return {
        "email": email.lower(),
        "first_name": me.get("first_name", "") or "",
        "last_name": me.get("last_name", "") or "",
    }


PROVIDERS = {"google": verify_google, "facebook": verify_facebook}