import time
from fastapi import Request
from utils.logger_config import log


async def log_request_middleware(request: Request, call_next):
    request_start_time = time.monotonic()
    response = await call_next(request)
    request_duration = time.monotonic() - request_start_time
    log_data = {"method": request.method, "path": request.url.path, "duration": request_duration}
    log.info(log_data)
    return response
