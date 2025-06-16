from typing import List, Type, Any, MutableMapping, Union

from aas_core3 import jsonization
from aas_core3.types import AssetAdministrationShell

from basyx import ObjectStore
from server.utils.error_handling import CustomErrorResponse


class AasService:
    def __init__(self, global_object_store: ObjectStore):
        self.obj_store = global_object_store

    # General helper functions
    def _get_all_shells(self) -> List[Type]:
        # FIXME: Type issues. Should this be casted to List[AAS]?
        return self.obj_store.get_identifiables_by_type(AssetAdministrationShell)

    def _get_shell_by_id(self, aas_identifier) -> AssetAdministrationShell:
        shell = self.obj_store.get(aas_identifier)
        if shell is None or not isinstance(shell, AssetAdministrationShell):
            raise CustomErrorResponse(status_code=404, message="Submodel with id " + aas_identifier + " not found")
        return shell

    def _jsonable_shells(self, submodels: List[AssetAdministrationShell]) \
            -> List[Union[bool, int, float, str, List[Any], MutableMapping[str, Any]]]:
        return [jsonization.to_jsonable(submodel) for submodel in submodels]

    # Endpoint specific logic
    def get_all_shells_as_jsonable(self) -> List[Union[bool, int, float, str, List[Any], MutableMapping[str, Any]]]:
        return self._jsonable_shells(self._get_all_shells())

    def get_shell_jsonable_by_id(self, aas_identifier):
        shell = self._get_shell_by_id(aas_identifier)
        return jsonization.to_jsonable(shell)

    def add_shell_from_body(self, json):
        shell = jsonization.asset_administration_shell_from_jsonable(json)
        try:
            self.obj_store.add(shell)
        except KeyError as e:
            raise CustomErrorResponse(status_code=400, exception=e)
        return {"message": "Shell processed"}

    def put_shell_by_id(self, aas_identifier, json):
        shell = self._get_shell_by_id(aas_identifier)
        new_shell = jsonization.asset_administration_shell_from_jsonable(json)
        if shell.id != new_shell.id:
            raise CustomErrorResponse(status_code=403, message="Shell with id " + aas_identifier + " does not match")
        self.obj_store.discard(shell)
        self.obj_store.add(new_shell)
        return jsonization.to_jsonable(new_shell)

    def delete_shell_by_id(self, aas_identifier):
        shell = self._get_shell_by_id(aas_identifier)
        self.obj_store.discard(shell)
        return {"message": "AssetAdministrationShell with id " + aas_identifier + " deleted successfully"}

    def get_asset_information_by_id_as_jsonable(self, aas_identifier):
        shell = self._get_shell_by_id(aas_identifier)
        return jsonization.to_jsonable(shell.asset_information)

    def put_asset_information_by_id_from_jsonable(self, aas_identifier, json):
        shell = self._get_shell_by_id(aas_identifier)
        self.obj_store.discard(shell)
        new_information = jsonization.asset_information_from_jsonable(json)
        shell.asset_information = new_information
        self.obj_store.add(shell)
        return jsonization.to_jsonable(shell)

    def get_thumbnail_by_id(self, aas_identifier):
        shell = self._get_shell_by_id(aas_identifier)
        return jsonization.to_jsonable(shell.asset_information.default_thumbnail)

    def put_thumbnail_by_id(self, aas_identifier, thumbnail):
        shell = self._get_shell_by_id(aas_identifier)
        self.obj_store.discard(shell)
        new_thumbnail = jsonization.resource_from_jsonable(thumbnail)
        shell.asset_information.default_thumbnail = new_thumbnail
        self.obj_store.add(shell)
        return jsonization.to_jsonable(shell.asset_information.default_thumbnail)

    def delete_thumbnail_by_id(self, ass_identifier):
        shell = self._get_shell_by_id(ass_identifier)
        self.obj_store.discard(shell)
        shell.asset_information.default_thumbnail = None
        self.obj_store.add(shell)
        return jsonization.to_jsonable(shell)