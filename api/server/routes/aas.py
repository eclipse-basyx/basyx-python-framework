from typing import Any

from aas_core3.types import Identifiable
from fastapi import APIRouter, Request, HTTPException

from server.services.aas_service import AasService
from basyx import ObjectStore

from server.utils.decorator import paginated

class AasRouter:
    def __init__(self, global_obj_store: ObjectStore[Identifiable]):
        self.router = APIRouter()
        self.service = AasService(global_obj_store)
        self._setup_routes()

    def _setup_routes(self):
        @self.router.get("/shells")
        @paginated()
        async def get_all_aas(request: Request) -> Any:
            return self.service.get_all_shells_as_jsonable()

        @self.router.post("/shells")
        async def create_aas(request: Request) -> Any:
            body = await request.json()
            return self.service.add_shell_from_body(body)

        @self.router.get("/shells/$reference")
        async def get_all_aas_reference() -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.get("/shells/{aas_identifier}")
        async def get_aas_by_id(aas_identifier: str) -> Any:
            return self.service.get_shell_jsonable_by_id(aas_identifier)

        @self.router.put("/shells/{aas_identifier}")
        async def put_aas(aas_identifier: str, request: Request) -> Any:
            # Update shell with given id
            body = await request.json()
            return self.service.put_shell_by_id(aas_identifier, body)

        @self.router.delete("/shells/{aas_identifier}")
        async def delete_aas(aas_identifier: str) -> Any:
            return self.service.delete_shell_by_id(aas_identifier)

        @self.router.get("/shells/{aas_identifier}/asset-information")
        async def get_aas_reference_by_id(aas_identifier: str) -> Any:
            return self.service.get_asset_information_by_id_as_jsonable(aas_identifier)

        @self.router.put("/shells/{aas_identifier}/asset-information")
        async def get_aas_reference_by_id(aas_identifier: str, request: Request) -> Any:
            body = await request.json()
            return self.service.put_asset_information_by_id_from_jsonable(aas_identifier, body)

        @self.router.get("/shells/{aas_identifier}/asset-information/thumbnail")
        async def get_aas_thumbnail_by_id(aas_identifier: str) -> Any:
            return self.service.get_thumbnail_by_id(aas_identifier)

        @self.router.put("/shells/{aas_identifier}/asset-information/thumbnail")
        async def get_aas_reference_by_id(aas_identifier: str, request: Request) -> Any:
            body = await request.json()
            return self.service.put_thumbnail_by_id(aas_identifier, body)

        @self.router.delete("/shells/{aas_identifier}/asset-information/thumbnail")
        async def delete_aas(aas_identifier: str) -> Any:
            return self.service.delete_thumbnail_by_id(aas_identifier)

        # TODO: Asset-information endpoints
        # /shells/{aas_identifier}/$reference GET
