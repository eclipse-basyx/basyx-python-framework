from typing import Any, MutableMapping, List, Union, Type

from aas_core3 import jsonization
from aas_core3.types import Submodel, SubmodelElement, AssetAdministrationShell

from basyx import ObjectStore
from server.utils.error_handling import CustomErrorResponse


class SubmodelService:
    def __init__(self, global_object_store: ObjectStore):
        self.obj_store = global_object_store

    # General helper functions
    def _get_all_submodels(self) -> List[Type]:
        return self.obj_store.get_identifiables_by_type(Submodel)

    def _get_all_submodel_references_by_shell(self, aas_identifier: str) -> List[Type]:
        shell = self.obj_store.get(aas_identifier)
        if isinstance(shell, AssetAdministrationShell):
            return shell.submodels  # FIXME: Typing issues, should this be (safe) casted?
        else:
            raise CustomErrorResponse(status_code=404, message="AAS " + aas_identifier + " not found")

    def _jsonable_submodels(self, submodels: List[Submodel]) \
            -> List[Union[bool, int, float, str, List[Any], MutableMapping[str, Any]]]:
        return [jsonization.to_jsonable(submodel) for submodel in submodels]

    def _get_submodel_by_id(self, submodel_id):
        submodel = self.obj_store.get(submodel_id)
        if submodel is None or not isinstance(submodel, Submodel):
            raise CustomErrorResponse(status_code=404, message="Submodel with id " + submodel_id + " not found")
        return submodel

    def _get_submodel_element_by_id_short(self, submodel_id, element_id_short):
        submodel = self._get_submodel_by_id(submodel_id)
        for element in submodel.descend():
            if isinstance(element, SubmodelElement):
                if element.id_short == element_id_short:
                    return element
        return None

    # Endpoint specific logic
    def get_all_submodels_as_jsonables(self) \
            -> List[Union[bool, int, float, str, List[Any], MutableMapping[str, Any]]]:
        return self._jsonable_submodels(self._get_all_submodels())

    def add_submodel_from_body(self, json):
        submodel = jsonization.submodel_from_jsonable(json)
        try:
            self.obj_store.add(submodel)
        except KeyError as e:
            raise CustomErrorResponse(status_code=400, exception=e)
        return {"message": "Submodel processed"}

    def get_submodel_jsonable_by_id(self, submodel_id: str):
        submodel = self._get_submodel_by_id(submodel_id)
        return jsonization.to_jsonable(submodel)

    def update_submodel_by_id(self, submodel_id: str, json):
        submodel = self._get_submodel_by_id(submodel_id)
        new_submodel = jsonization.submodel_from_jsonable(json)
        if submodel.id != new_submodel.id:
            raise CustomErrorResponse(status_code=403, message="Submodel with id " + submodel_id + " does not match")
        self.obj_store.discard(submodel)
        self.obj_store.add(new_submodel)
        return jsonization.to_jsonable(new_submodel)

    def delete_submodel_by_id(self, submodel_id):
        submodel = self._get_submodel_by_id(submodel_id)
        self.obj_store.discard(submodel)
        return {"message": "Submodel with id " + submodel_id + " deleted successfully"}

    def get_submodel_elements(self, submodel_id):
        # FIXME: Has to respect hierarchy!!
        submodel = self._get_submodel_by_id(submodel_id)
        elements = []
        for element in submodel.descend():
            # Maybe filter some items out?
            elements.append(jsonization.to_jsonable(element))
        return elements

    def update_submodel_elements(self, submodel_id, json):
        submodel = self._get_submodel_by_id(submodel_id)
        new_elements = []
        for element in json:
            deserialized_element = jsonization.submodel_element_from_jsonable(element)
            new_elements.append(deserialized_element)
        self.obj_store.discard(submodel)
        submodel.submodel_elements = new_elements
        self.obj_store.add(submodel)

    def get_submodel_element(self, submodel_id, element_short_id):
        element = self._get_submodel_element_by_id_short(submodel_id, element_short_id)
        if element is None:
            raise CustomErrorResponse(status_code=404, message="Submodel element with id " + element_short_id + " not found.")
        return jsonization.to_jsonable(element)

    def post_submodel_element(self, submodel_id, body):
        submodel = self._get_submodel_by_id(submodel_id)
        submodel_element = jsonization.submodel_element_from_jsonable(body)
        existing_submodel_element = self._get_submodel_element_by_id_short(submodel_id, submodel_element.id_short)
        if existing_submodel_element is None:
            submodel.submodel_elements.append(submodel_element)
            return jsonization.to_jsonable(submodel_element)
        else:
            raise CustomErrorResponse(status_code=400,
                                message="Submodel element with id " + submodel_element.id_short + " already exists")

    def put_submodel_element(self, submodel_id, body):
        submodel = self._get_submodel_by_id(submodel_id)
        submodel_element = jsonization.submodel_element_from_jsonable(body)
        existing_submodel_element = self._get_submodel_element_by_id_short(submodel_id, submodel_element.id_short)
        if existing_submodel_element is None:
            raise CustomErrorResponse(status_code=404,
                                message="Submodel element with id " + submodel_element.id_short + " does not exist")
        else:
            submodel.submodel_elements.remove(existing_submodel_element)
            submodel.submodel_elements.append(submodel_element)
            return jsonization.to_jsonable(submodel_element)

    def delete_submodel_element(self, submodel_id, id_short):
        submodel = self._get_submodel_by_id(submodel_id)
        existing_submodel_element = self._get_submodel_element_by_id_short(submodel_id, id_short)
        if existing_submodel_element is None:
            raise CustomErrorResponse(status_code=404, message="Submodel element with id " + id_short + " does not exist")
        else:
            submodel.submodel_elements.remove(existing_submodel_element)
            return jsonization.to_jsonable(existing_submodel_element)
