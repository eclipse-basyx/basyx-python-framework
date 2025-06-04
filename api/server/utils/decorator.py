from functools import wraps
from fastapi import Request
from typing import Callable, Any, Union


def limited(default_limit: int = 100):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Extract request from kwargs (FastAPI automatically passes it)
            request: Request = kwargs.get("request")
            limit: Union[str, int] = request.query_params.get("limit", default_limit)

            try:
                limit = int(limit)  # Ensure limit is an integer
            except ValueError:
                limit = default_limit  # Fallback if conversion fails

            # Call the original function
            result = await func(*args, **kwargs)

            # Apply limit if the result is a list
            if isinstance(result, list):
                return result[:limit]
            return result  # If not a list, return as-is

        return wrapper

    return decorator

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
