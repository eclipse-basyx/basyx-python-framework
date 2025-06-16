from typing import Iterable, Any


class Pagination:
    # TODO: Add cursor
    def paginate(self, collection: Iterable[Any], limit: int) -> Iterable[Any]:
        return list(collection)[:limit]
