from typing import Any, MutableMapping, List, Union

from aas_core3 import jsonization
from aas_core3.types import Submodel, ConceptDescription

from basyx import ObjectStore
from server.utils.error_handling import CustomErrorResponse


class SubmodelRegistryServerService:
    def __init__(self, global_object_store: ObjectStore):
        self.obj_store = global_object_store

    def get_all_submodel_descriptors(self) -> List[str]:
        #print(self.obj_store.__dict__)

        all_descriptors = self.obj_store.get_identifiables_by_type(ConceptDescription)
        #print(all_descriptors.__dict__)
        print(all_descriptors)
        #print("test")
        submodel_descriptors_store = ObjectStore()
        for descriptor in all_descriptors:
            reference_list = descriptor.is_case_of
            print(reference_list)
            for element in reference_list:
                reference_ids = element.keys
                print(reference_ids)
                for reference_id in reference_ids:
                    try:
                        identifiable = self.obj_store.get_identifiable(reference_id.value)
                    except KeyError as e:
                        # TODO: Handle error? Or is this intended?
                        identifiable = []
                    if isinstance(identifiable, Submodel):
                        try:
                            submodel_descriptors_store.add(descriptor)
                        except KeyError as e:
                            pass
        return [jsonization.to_jsonable(descriptor) for descriptor in submodel_descriptors_store]

    def get_submodel_descriptor_by_id(self, descriptor_id) \
            -> List[Union[bool, int, float, str, List[Any], MutableMapping[str, Any]]]:
        try:
            aas_descriptor = self.obj_store.get_identifiable(descriptor_id)
        except KeyError as e:
            raise CustomErrorResponse(status_code=400, exception=e)
        assert isinstance(aas_descriptor, ConceptDescription)
        return jsonization.to_jsonable(aas_descriptor)

    def post_submodel_descriptor(self, json):
        submodel_descriptor = jsonization.concept_description_from_jsonable(json)

        # Check if all referenced submodels exist in the obeject_store

        for reference in submodel_descriptor.is_case_of:
            reference_ids = reference.keys
            for reference_id in reference_ids:
                try:
                    self.obj_store.get_identifiable(reference_id.value)
                except KeyError as e:
                    raise CustomErrorResponse(status_code=400, message="A referenced submodel of the concept description "
                                                                 "with the following id does not exist in the "
                                                                 "object_store", exception=e)

        try:
            self.obj_store.add(submodel_descriptor)
        except KeyError as e:
            raise CustomErrorResponse(status_code=400, detail="A referenced submodel of the concept description "
                                                        "with the following id does not exist in the "
                                                        "object_store:", exception=e)
        return {"message": "Submodel descriptor processed"}

    def put_submodel_descriptor_by_id(self, json):
        submodel_descriptor = jsonization.concept_description_from_jsonable(json)

        # Check if all referenced submodels exist in the obeject_store

        for reference in submodel_descriptor.is_case_of:
            reference_ids = reference.keys
            for reference_id in reference_ids:
                try:
                    self.obj_store.get_identifiable(reference_id.value)
                except KeyError as e:
                    raise CustomErrorResponse(status_code=400, detail= "A referenced submodel of the concept description "
                                                                 "with the following id does not exist in the "
                                                                 "object_store:", exception=e)

        try:
            self.obj_store.delete(submodel_descriptor.id)  # should there be an exception if there is no aasx_package to
            # update?
            self.obj_store.add(submodel_descriptor)
        except KeyError as e:
            raise CustomErrorResponse(status_code=400, exception=e)
        return {"message": "AASX package updated"}

    def delete_submodel_descriptor_by_id(self, descriptor_id):
        try:
            self.obj_store.delete(descriptor_id)  # should there be an exception if there is no aasx_package to delete?
        except KeyError as e:
            raise CustomErrorResponse(status_code=400, exception=e)
        return {"message": "Submodel descriptor deleted"}
