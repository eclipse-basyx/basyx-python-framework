import traceback
from fastapi import HTTPException

class CustomErrorResponse(HTTPException):
    def __init__(self, exception: Exception = Exception("No exception provided"),
                 message: str = "No additional information was provided.", status_code: int = 400):
        super().__init__(
            status_code=status_code,
            detail={
                "message": message,
                "error": str(exception),
                "stacktrace": traceback.format_exc(),
            },
        )
