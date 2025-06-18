from typing import Any

from aas_core3.types import Identifiable
from fastapi import APIRouter, Request

from server.services.aas_registry_server_service import AasRegistryServerService
from basyx import ObjectStore

from server.utils.decorator import paginated


class AasRegistryRouter:
    def __init__(self, global_obj_store: ObjectStore[Identifiable]):
        self.router = APIRouter()
        self.obj_store = global_obj_store
        self.service = AasRegistryServerService(global_obj_store)
        self._setup_routes()

    def _setup_routes(self):
        @self.router.get("/")
        @paginated()
        async def get_all_aas_descriptors(request: Request) -> Any:
            return self.service.get_all_asset_administration_shell_descriptors()

        @self.router.get("/{aas_descriptor_id}")
        async def get_aas_descriptor_by_id(aas_descriptor_id: str) -> Any:
            return self.service.get_asset_administration_shell_descriptor_by_id(aas_descriptor_id)

        @self.router.post("/")
        async def post_aas_descriptor(request: Request) -> Any:
            body = await request.json()
            return self.service.post_asset_administration_shell_descriptor(body)

        @self.router.put("/")
        async def put_aas_descriptor(request: Request) -> Any:
            body = await request.json()
            return self.service.put_asset_administration_shell_descriptor_by_id(body)

        @self.router.delete("/{aas_descriptor_id}")
        async def delete_aas_descriptor_by_id(aas_descriptor_id: str) -> Any:
            return self.service.delete_asset_administration_shell_descriptor_by_id(aas_descriptor_id)
