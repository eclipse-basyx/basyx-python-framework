from typing import Any, Iterable

from aas_core3.types import Identifiable
from fastapi import APIRouter, Request, HTTPException

from server.services.submodel_service import SubmodelService
from basyx import ObjectStore

from server.utils.pagination import Pagination
from server.utils.decorator import limited


class SubmodelRouter(Pagination):
    def __init__(self, global_obj_store: ObjectStore[Identifiable]):
        self.router = APIRouter()
        self.obj_store = global_obj_store
        self.service = SubmodelService(global_obj_store)
        self._setup_routes()

    def _setup_routes(self):
        # GetAllSubmodels and path-suffixes
        @self.router.get("")
        @limited()
        async def get_submodel_all(request: Request) -> Any:
            return self.service.get_all_submodels_as_jsonables()

        @self.router.get("/$metadata")
        @limited()
        async def get_submodel_all_metadata(request: Request) -> Any:
            # Returns metadata for all submodels, stripped of detailed content
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.get("/$reference")
        @limited()
        async def get_submodel_all_reference(request: Request) -> Any:
            # Returns references for all submodels without full data
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.get("/$value")
        @limited()
        async def not_implemented_value(request: Request) -> Any:
            raise HTTPException(status_code=501, detail="This route is not implemented!")

        @self.router.get("/$path")
        async def not_implemented_path() -> Any:
            raise HTTPException(status_code=501, detail="This route is not implemented!")

        @self.router.post("")
        async def post_submodel(request: Request) -> Any:
            body = await request.json()
            return self.service.add_submodel_from_body(body)

        @self.router.get("/{submodel_identifier}")
        async def get_submodel(submodel_identifier: str) -> Any:
            return self.service.get_submodel_jsonable_by_id(submodel_identifier)

        @self.router.put("/{submodel_identifier}")
        async def put_submodel(submodel_identifier: str, request: Request) -> Any:
            # Update submodel with given id
            body = await request.json()
            return self.service.update_submodel_by_id(submodel_identifier, body)

        @self.router.patch("/{submodel_identifier}")
        async def not_implemented_patch_submodel(submodel_identifier: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not implemented!")

        @self.router.delete("/{submodel_identifier}")
        async def delete_submodel(submodel_identifier: str) -> Any:
            return self.service.delete_submodel_by_id(submodel_identifier)

        # Nested routes for each submodel (PUT/PATCH x $metadata/$value/$reference/$path)
        @self.router.get("/{submodel_identifier}/$metadata")
        async def get_submodels_metadata(submodel_identifier: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.patch("/{submodel_identifier}/$metadata")
        async def not_implemented_metadata_patch(submodel_identifier: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.get("/{submodel_identifier}/$value")
        async def not_implemented_value_get(submodel_identifier: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.patch("/{submodel_identifier}/$value")
        async def not_implemented_value_patch(submodel_identifier: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is yet implemented!")

        @self.router.get("/{submodel_identifier}/$reference")
        async def get_submodels_reference(submodel_identifier: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.get("/{submodel_identifier}/$path")
        async def not_implemented_path_get(submodel_identifier: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is yet implemented!")

        @self.router.post("/{submodel_identifier}/submodel-elements")
        async def post_submodel_elements(submodel_identifier: str, request: Request) -> Any:
            body = await request.json()
            return self.service.post_submodel_element(submodel_identifier, body)

        @self.router.get("/{submodel_identifier}/submodel-elements")
        async def get_submodel_submodel_elements(submodel_identifier: str) -> Any:
            # Get submodel elements
            self.service.get_submodel_elements(submodel_identifier)

        # GetSubmodelElement and path-suffixes
        @self.router.get("/{submodel_identifier}/submodel-elements/$metadata")
        async def get_submodel_submodel_elements_metadata(submodel_identifier: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.get("/{submodel_identifier}/submodel-elements/$reference")
        async def get_submodel_submodel_elements_reference(submodel_identifier: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.get("/{submodel_identifier}/submodel-elements/$value")
        async def not_implemented_submodel_elements_value(submodel_identifier: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.get("/{submodel_identifier}/submodel-elements/$path")
        async def not_implemented_submodel_elements_path(submodel_identifier: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.get("/{submodel_identifier}/submodel-elements/{id_short_path}")
        async def get_submodel_submodel_elements_id_short_path(submodel_identifier: str, id_short_path: str) -> Any:
            return self.service.get_submodel_element(submodel_identifier, id_short_path)

        @self.router.post("/{submodel_identifier}/submodel-elements/{id_short_path}")
        async def post_submodel_submodel_elements_id_short_path(submodel_identifier: str, request: Request) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.put("/{submodel_identifier}/submodel-elements/{id_short_path}")
        async def put_submodel_submodel_elements_id_short_path(submodel_identifier: str, request: Request) -> Any:
            body = await request.json()
            return self.service.put_submodel_element(submodel_identifier, body)

        @self.router.patch("/{submodel_identifier}/submodel-elements/{id_short_path}")
        async def not_implemented_patch_submodel_submodel_elements_id_short_path(submodel_identifier: str,
                                                                                 id_short_path: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.delete("/{submodel_identifier}/submodel-elements/{id_short_path}")
        async def delete_submodel_submodel_elements_id_short_path(submodel_identifier: str, id_short_path: str) -> Any:
            return self.service.delete_submodel_element(submodel_identifier, id_short_path)

        @self.router.get("/{submodel_identifier}/submodel-elements/{id_short_path}/$metadata")
        async def get_submodel_submodel_elements_id_short_path_metadata(submodel_identifier: str, id_short_path: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.patch("/{submodel_identifier}/submodel-elements/{id_short_path}/$metadata")
        async def not_implemented_metadata_patch(submodel_identifier: str, id_short_path: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.get("/{submodel_identifier}/submodel-elements/{id_short_path}/$reference")
        async def get_submodel_submodel_elements_id_short_path_reference(submodel_identifier: str, id_short_path: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.get("/{submodel_identifier}/submodel-elements/{id_short_path}/$value")
        async def not_implemented_value_get(submodel_identifier: str, id_short_path: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.patch("/{submodel_identifier}/submodel-elements/{id_short_path}/$value")
        async def not_implemented_value_patch(submodel_identifier: str, id_short_path: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.get("/{submodel_identifier}/submodel-elements/{id_short_path}/attachment")
        async def get_submodel_submodel_element_attachment(submodel_identifier: str, id_short_path: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.put("/{submodel_identifier}/submodel-elements/{id_short_path}/attachment")
        async def put_submodel_submodel_element_attachment(submodel_identifier: str, id_short_path: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.delete("/{submodel_identifier}/submodel-elements/{id_short_path}/attachment")
        async def delete_submodel_submodel_element_attachment(submodel_identifier: str, id_short_path: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.post("/{submodel_identifier}/submodel-elements/{id_short_path}/invoke")
        async def not_implemented_invoke(submodel_identifier: str, id_short_path: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.post("/{submodel_identifier}/submodel-elements/{id_short_path}/invoke/$value")
        async def not_implemented_invoke_value(submodel_identifier: str, id_short_path: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.post("/{submodel_identifier}/submodel-elements/{id_short_path}/invoke-async")
        async def not_implemented_invoke_async(submodel_identifier: str, id_short_path: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.post("/{submodel_identifier}/submodel-elements/{id_short_path}/invoke-async/$value")
        async def not_implemented_invoke_async_value(submodel_identifier: str, id_short_path: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.get("/{submodel_identifier}/submodel-elements/{id_short_path}/qualifiers")
        async def get_submodel_submodel_element_qualifiers(submodel_identifier: str, id_short_path: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.post("/{submodel_identifier}/submodel-elements/{id_short_path}/qualifiers")
        async def post_submodel_submodel_element_qualifiers(submodel_identifier: str, id_short_path: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.get("/{submodel_identifier}/submodel-elements/{id_short_path}/qualifiers/{qualifier_type}")
        async def get_submodel_submodel_element_qualifiers_specific(submodel_identifier: str, id_short_path: str,
                                                                    qualifier_type: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.put("/{submodel_identifier}/submodel-elements/{id_short_path}/qualifiers/{qualifier_type}")
        async def put_submodel_submodel_element_qualifiers(submodel_identifier: str, id_short_path: str,
                                                           qualifier_type: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        @self.router.delete("/{submodel_identifier}/submodel-elements/{id_short_path}/qualifiers/{qualifier_type}")
        async def delete_submodel_submodel_element_qualifiers(submodel_identifier: str, id_short_path: str,
                                                              qualifier_type: str) -> Any:
            raise HTTPException(status_code=501, detail="This route is not yet implemented!")

        # FIXME: Missing based on swaggerhub:
        # - /shells/{aasIdentifier}/submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/operation-status/{handleId}
        # - /shells/{aasIdentifier}/submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/operation-results/{handleId}
        # - /shells/{aasIdentifier}/submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/operation-results/{handleId}/$value
