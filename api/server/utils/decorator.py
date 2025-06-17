from functools import wraps
from fastapi import Request
from typing import Callable, Any, Union, Tuple


def paginated(default_limit: int = 100):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            request: Request = kwargs.get("request")
            query = request.query_params

            try:
                limit = int(query.get("limit", default_limit))
                cursor = int(query.get("cursor", 0))
                if limit < 0 or cursor < 0:
                    raise ValueError
            except ValueError:
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="Cursor and limit must be >0")

            result = await func(*args, **kwargs)

            if isinstance(result, list):
                # FIXME: Is this correct? Following Spec p.119
                return {
                    "result": result[cursor:cursor + limit],
                    "paging_metadata": {
                        "next_cursor": cursor + limit if cursor + limit < len(result) else None
                    }
                }

            return result

        return wrapper

    return decorator
