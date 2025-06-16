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
