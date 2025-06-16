from typing import Any, MutableMapping, List, Union

from aas_core3 import jsonization
from aas_core3.types import AssetAdministrationShell, ConceptDescription

from basyx import ObjectStore
from server.utils.error_handling import CustomErrorResponse


class AasRegistryServerService:
    def __init__(self, global_object_store: ObjectStore):
        self.obj_store = global_object_store

    def get_all_asset_administration_shell_descriptors(self) -> List[str]:
        all_descriptors = self.obj_store.get_identifiables_by_type(ConceptDescription)
        # print(all_descriptors.__dict__)
        # print(all_descriptors)
        # print("test")
        aas_descriptors_store = ObjectStore()
        for descriptor in all_descriptors:
            reference_list = descriptor.is_case_of
            print(reference_list)
            for element in reference_list:
                reference_ids = element.keys
                for reference_id in reference_ids:
                    try:
                        identifiable = self.obj_store.get_identifiable(reference_id)
                    except KeyError as e:
                        raise CustomErrorResponse(status_code=400, exception=e)

                    if isinstance(identifiable, AssetAdministrationShell):
                        try:
                            aas_descriptors_store.add(descriptor)
                        except KeyError as e:
                            pass
        return [jsonization.to_jsonable(descriptor) for descriptor in aas_descriptors_store]

    def get_asset_administration_shell_descriptor_by_id(self, descriptor_id) \
            -> List[Union[bool, int, float, str, List[Any], MutableMapping[str, Any]]]:
        aas_descriptor = self.obj_store.get_identifiable(descriptor_id)
        assert isinstance(aas_descriptor, ConceptDescription)
        return jsonization.to_jsonable(aas_descriptor)

    def post_asset_administration_shell_descriptor(self, json):
        aas_descriptor = jsonization.concept_description_from_jsonable(json)
        try:
            self.obj_store.add(aas_descriptor)
        except KeyError as e:
            raise CustomErrorResponse(status_code=400, exception=e)
        return {"message": "AAS Descriptor processed"}

    def put_asset_administration_shell_descriptor_by_id(self, json):
        aas_descriptor = jsonization.asset_administration_shell_from_jsonable(json)
        try:
            self.obj_store.delete(aas_descriptor.id)  # should there be an exception if there is no aasx_package to
            # update?
            self.obj_store.add(aas_descriptor)
        except KeyError as e:
            raise CustomErrorResponse(status_code=400, exception=e)
        return {"message": "AASX package updated"}

    def delete_asset_administration_shell_descriptor_by_id(self, descriptor_id):
        try:
            self.obj_store.delete(descriptor_id)  # should there be an exception if there is no aasx_package to delete?
        except KeyError as e:
            raise CustomErrorResponse(status_code=400, exception=e)
        return {"message": "AASX descriptor deleted"}
