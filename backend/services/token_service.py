from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from fastapi import Depends

from backend.services.auth_service import (
    verify_token
)

security = HTTPBearer()


def get_current_email(

    credentials: HTTPAuthorizationCredentials = Depends(
        security
    )

):

    token = credentials.credentials

    return verify_token(token)