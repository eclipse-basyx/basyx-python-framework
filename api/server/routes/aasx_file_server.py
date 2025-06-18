from typing import Any

from aas_core3.types import Identifiable
from fastapi import APIRouter, Request

from server.services.aasx_file_server_service import AasxFileServerService
from basyx import ObjectStore

from server.utils.decorator import paginated


class AasxFileServerRouter:
    def __init__(self, global_obj_store: ObjectStore[Identifiable]):
        self.router = APIRouter()
        self.obj_store = global_obj_store
        self.service = AasxFileServerService(global_obj_store)
        self._setup_routes()

    def _setup_routes(self):
        @self.router.get("")
        @paginated()
        async def get_all_aasx(request: Request) -> Any:
            return self.service.get_all_aasx_package_ids()

        @self.router.get("/{aasx_package_id}")
        async def get_aasx_by_package_id(aasx_package_id: str) -> Any:
            return self.service.get_aasx_by_package_id(aasx_package_id)

        @self.router.post("")
        async def post_aasx_package(request: Request) -> Any:
            body = await request.json()
            return self.service.post_aasx_package(body)

        @self.router.put("")
        async def put_assx_package(request: Request) -> Any:
            body = await request.json()
            return self.service.put_aasx_by_package_id(body)

        @self.router.delete("/{aasx_package_id}")
        async def delete_aasx_package_by_id(aasx_package_id: str) -> Any:
            return self.service.delete_aasx_by_package_id(aasx_package_id)
        