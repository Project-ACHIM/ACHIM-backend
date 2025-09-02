from typing import Any
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, date

def _convert(obj: Any):
    if isinstance(obj, BaseModel):
        return obj.dict()
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, list):
        return [_convert(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _convert(v) for k, v in obj.items()}
    return obj

def success_response(data: Any, message: str = "success"):
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": _convert(data),
            "message": message
        }
    )


def error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "status_code": status_code,
                "message": message
            }
        }
    )