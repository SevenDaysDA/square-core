import secrets

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from .config import API_KEY, API_KEY_HEADER_NAME
from .messages import AUTH_REQ, NO_API_KEY

import logging

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)


def validate_request(header: str = Security(api_key_header),) -> bool:
    if header is None:
        logger.info("Attempted access without API Key")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=NO_API_KEY.format(API_KEY_HEADER_NAME), headers={}
        )
    elif not secrets.compare_digest(header, str(API_KEY)):
        logger.info(f"Attempted access with wrong API Key {header}")
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=AUTH_REQ, headers={}
        )
    logger.info("Successful authorization with API Key")
    return True