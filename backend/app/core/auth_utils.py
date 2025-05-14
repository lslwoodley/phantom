# import base64
# import json
# import logging


# def get_authenticated_user_details(request_headers):
#     user_object = {}

#     # check the headers for the Principal-Id (the guid of the signed in user)
#     if "x-ms-client-principal-id" not in request_headers:
#         logging.info("No user principal found in headers")
#         # if it's not, assume we're in development mode and return a default user
#         from . import sample_user

#         raw_user_object = sample_user.sample_user
#     else:
#         # if it is, get the user details from the EasyAuth headers
#         raw_user_object = {k: v for k, v in request_headers.items()}

#     normalized_headers = {k.lower(): v for k, v in raw_user_object.items()}
#     user_object["user_principal_id"] = normalized_headers.get(
#         "x-ms-client-principal-id"
#     )
#     user_object["user_name"] = normalized_headers.get("x-ms-client-principal-name")
#     user_object["auth_provider"] = normalized_headers.get("x-ms-client-principal-idp")
#     user_object["auth_token"] = normalized_headers.get("x-ms-token-aad-id-token")
#     user_object["client_principal_b64"] = normalized_headers.get(
#         "x-ms-client-principal"
#     )
#     user_object["aad_id_token"] = normalized_headers.get("x-ms-token-aad-id-token")

#     return user_object


# def get_tenantid(client_principal_b64):
#     logger = logging.getLogger(__name__)
#     tenant_id = ""
#     if client_principal_b64:
#         try:
#             # Decode the base64 header to get the JSON string
#             decoded_bytes = base64.b64decode(client_principal_b64)
#             decoded_string = decoded_bytes.decode("utf-8")
#             # Convert the JSON string1into a Python dictionary
#             user_info = json.loads(decoded_string)
#             # Extract the tenant ID
#             tenant_id = user_info.get("tid")  # 'tid' typically holds the tenant ID
#         except Exception as ex:
#             logger.exception(ex)
#     return tenant_id



import logging
from typing import Dict, Any
from fastapi import Request, HTTPException, Depends
from jose import jwt, JWTError
import requests
from app_config import config

logger = logging.getLogger(__name__)

JWKS_CACHE: Dict[str, Any] = {}


def fetch_jwks() -> Dict[str, Any]:
    """Fetch the JWKS from Azure AD OpenID endpoint."""
    openid_config_url = f"https://login.microsoftonline.com/{config.AZURE_TENANT_ID}/v2.0/.well-known/openid-configuration"
    response = requests.get(openid_config_url)
    response.raise_for_status()
    jwks_uri = response.json().get("jwks_uri")
    logger.info(f"Fetching JWKS from {jwks_uri}")
    jwks_response = requests.get(jwks_uri)
    jwks_response.raise_for_status()
    return jwks_response.json()


def get_jwks() -> Dict[str, Any]:
    """Cache and return JWKS."""
    if not JWKS_CACHE:
        JWKS_CACHE.update(fetch_jwks())
    return JWKS_CACHE


def get_bearer_token(request: Request) -> str:
    """Extract Bearer token from Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
    return auth_header.split("Bearer ")[1]


def validate_bearer_token(token: str) -> Dict[str, Any]:
    """Validate Bearer token using Azure AD JWKS."""
    try:
        jwks = get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise HTTPException(status_code=401, detail="Invalid token - Key not found")

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=config.AZURE_CLIENT_ID,
            issuer=f"https://sts.windows.net/{config.AZURE_TENANT_ID}/"
        )
        return payload
    except JWTError as e:
        logger.error(f"Token validation failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user_claims(request: Request) -> Dict[str, Any]:
    """Dependency to extract claims."""
    token = get_bearer_token(request)
    return validate_bearer_token(token)


async def get_current_user_groups(claims: Dict[str, Any] = Depends(get_current_user_claims)) -> list:
    """Dependency to extract user's group claims."""
    return claims.get("groups", [])
