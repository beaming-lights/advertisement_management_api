from dependencies.authn import authenticated_user
from fastapi import Depends, HTTPException, status
from typing import Annotated


def has_role(role):
    def check_role(user: Annotated[any, Depends(authenticated_user)]):
        if not role == user.role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"user does not have {role} role")
    return check_role