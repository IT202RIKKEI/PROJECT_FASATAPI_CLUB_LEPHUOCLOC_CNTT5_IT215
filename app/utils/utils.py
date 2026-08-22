from fastapi import Request, Path
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Any


def create_response(status_code: int,
                    message: str,
                    request: Request,
                    error: Any | None = None,
                    data: Any | None = None,
                    ) -> JSONResponse:

    response_content = {
        "status_code": status_code,
        "message": message,
        "error": error,
        "data": data,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "path": request.url.path
    }

    return JSONResponse(status_code=status_code, content=response_content)
