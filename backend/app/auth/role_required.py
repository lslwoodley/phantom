# 📄 roles_required.py
# 📍 Location: backend/app/auth/roles_required.py
# 🧠 Purpose: Decorator utility to enforce Entra ID role-based access for Phantom endpoints

from fastapi import Depends, HTTPException, status
from app.auth.msal_auth import EntraRBAC
from app.config import ROLE_GROUPS
from typing import List, Callable, Union

# Define reusable decorator for role enforcement
def roles_required(allowed: Union[str, List[str]]) -> Callable:
    async def role_checker(claims: dict = Depends(EntraRBAC())) -> dict:
        user_roles = claims.get("roles", [])

        # Resolve role group name to role list if needed
        if isinstance(allowed, str):
            allowed_roles = ROLE_GROUPS.get(allowed, [])
        else:
            allowed_roles = allowed

        if any(role in user_roles for role in allowed_roles):
            return claims

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: requires one of {allowed_roles}"
        )

    return role_checker

# ✅ Example usage:
# @app.get("/secure")
# async def admin_view(claims: dict = Depends(roles_required("phantom_admin"))):
#     return {"user": claims["preferred_username"], "roles": claims.get("roles", [])}
