from typing import Any

from aas_core3.types import Identifiable
from fastapi import APIRouter, Request

from server.services.submodel_registry_server_service import SubmodelRegistryServerService
from basyx import ObjectStore

from server.utils.decorator import paginated


class SubmodelRegistryRouter:
    def __init__(self, global_obj_store: ObjectStore[Identifiable]):
        self.router = APIRouter()
        self.obj_store = global_obj_store
        self.service = SubmodelRegistryServerService(global_obj_store)
        self._setup_routes()

    def _setup_routes(self):
        @self.router.get("/")
        @paginated()
        async def get_all_submodel_descriptors() -> Any:
            return self.service.get_all_submodel_descriptors()

        @self.router.get("/{submodel_id}")
        async def get_submodel_descriptor_by_id(submodel_id: str) -> Any:
            return self.service.get_submodel_descriptor_by_id(submodel_id)

        @self.router.post("/")
        async def post_submodel_descriptor(request: Request) -> Any:
            body = await request.json()
            return self.service.post_submodel_descriptor(body)

        @self.router.put("/")
        async def put_submodel_descriptor_by_id(request: Request) -> Any:
            body = await request.json()
            return self.service.put_submodel_descriptor_by_id(body)

        @self.router.delete("/{submodel_id}")
        async def delete_submodel_descriptor_by_id(submodel_id: str) -> Any:
            return self.service.delete_submodel_descriptor_by_id(submodel_id)
