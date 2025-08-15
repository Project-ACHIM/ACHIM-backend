import time
import logging
import traceback
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from backend.core.errors import AppException

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """全リクエストの処理時間・メソッド・パス・ステータスコードを記録"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000  # ms
        logger.info(
            f"{request.method} {request.url.path} "
            f"-> {response.status_code} [{process_time:.2f}ms]"
        )
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """AppException とその他例外を統一フォーマットで返す"""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)

        except AppException as e:
            logger.warning(f"Handled AppException: {e.message}")
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "error": {"status_code": e.status_code, "message": e.message},
                },
            )

        except Exception as e:
            logger.exception("Unexpected error occurred")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "status_code": 500,
                        "message": "サーバーエラーが発生しました",
                    },
                },
            )
