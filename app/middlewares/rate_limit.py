import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request


def make_limiter(max_requests: int, window_seconds: int = 600):
    """Per-IP, in-memory limiter used as a FastAPI dependency on public endpoints."""
    hits = defaultdict(deque)

    def limiter(request: Request):
        ip = request.client.host if request.client else 'unknown'
        now = time.time()
        queue = hits[ip]
        while queue and now - queue[0] > window_seconds:
            queue.popleft()
        if len(queue) >= max_requests:
            raise HTTPException(status_code=429, detail='Too many requests. Please try again later.')
        queue.append(now)

    return limiter


contact_rate_limit = make_limiter(5)
form_rate_limit = make_limiter(10)
give_rate_limit = make_limiter(10)
