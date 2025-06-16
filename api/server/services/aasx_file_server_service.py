from typing import Any, MutableMapping, List, Union

from aas_core3.types import AssetAdministrationShell
from aas_core3 import jsonization

from basyx import ObjectStore
from server.utils.error_handling import CustomErrorResponse


class AasxFileServerService:
    def __init__(self, global_object_store: ObjectStore):
        self.obj_store = global_object_store

    def get_all_aasx_package_ids(self) -> List[str]:
        return [item.id for item in self.obj_store if isinstance(item, AssetAdministrationShell)]

    def get_aasx_by_package_id(self, package_id) \
            -> List[Union[bool, int, float, str, List[Any], MutableMapping[str, Any]]]:
        aasx_package = self.obj_store.get_identifiable(package_id)
        assert isinstance(aasx_package, AssetAdministrationShell)
        return jsonization.to_jsonable(aasx_package)

    def post_aasx_package(self, json):
        aasx_package = jsonization.asset_administration_shell_from_jsonable(json)
        try:
            self.obj_store.add(aasx_package)
        except KeyError as e:
            raise CustomErrorResponse(status_code=400, exception=e)
        return {"message": "AASX package processed"}

    def put_aasx_by_package_id(self, json):
        aasx_package = jsonization.asset_administration_shell_from_jsonable(json)
        try:
            self.obj_store.delete(aasx_package.id)  # should there be an exception if there is no aasx_package to
            # update?
            self.obj_store.add(aasx_package)
        except KeyError as e:
            raise CustomErrorResponse(status_code=400, exception=e)
        return {"message": "AASX package updated"}

    def delete_aasx_by_package_id(self, package_id):
        try:
            self.obj_store.delete(package_id)  # should there be an exception if there is no aasx_package to delete?
        except KeyError as e:
            raise CustomErrorResponse(status_code=400, exception=e)
        return {"message": "AASX package deleted"}
