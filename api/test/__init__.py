def wrap_paginated(result):
    return {
        "result": result,
        "paging_metadata": {
            "next_cursor": None
        }
    }
