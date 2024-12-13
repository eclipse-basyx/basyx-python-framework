# Copyright (c) 2024 the Eclipse BaSyx Authors
#
# This program and the accompanying materials are made available under the terms of the MIT License, available in
# the LICENSE file of this project.
#
# SPDX-License-Identifier: MIT

from basyx.object_store import ObjectStore
from aas_core3.types import Identifiable, AssetAdministrationShell, AssetInformation, AssetKind
from basyx import model as aas_types

aas = AssetAdministrationShell(id="urn:x-test:aas1",
                               asset_information=AssetInformation(asset_kind=AssetKind.TYPE))

some_element = aas_types.Property(
    id_short="some_property",
    value_type=aas_types.DataTypeDefXSD.INT,
    value="1984"
)

another_element = aas_types.Blob(
    id_short="some_blob",
    content_type="application/octet-stream",
    value=b'\xDE\xAD\xBE\xEF'
)

list_element = aas_types.Blob(
    id_short="list_1",
    content_type="application/octet-stream",
    value=b'\xDE\xAD\xBE\xEF'
)

another_list_element = aas_types.Blob(
    id_short="list_2",
    content_type="application/octet-stream",
    value=b'\xDE\xAD\xBE\xEF'
)

element_list = aas_types.SubmodelElementList(id_short='ExampleSubmodelList',
                                             type_value_list_element=aas_types.AASSubmodelElements.
                                             SUBMODEL_ELEMENT_LIST,
                                             value=[list_element, another_list_element])

submodel1 = aas_types.Submodel(
    id="urn:x-test:submodel1",
    submodel_elements=[
        some_element,
        another_element,
        element_list
    ]
)
submodel2 = aas_types.Submodel(
    id="urn:x-test:submodel2",
    submodel_elements=[
        some_element
    ]
)

obj_store: ObjectStore[Identifiable] = ObjectStore()
obj_store.add(aas)
obj_store.add(submodel1)
obj_store.add(submodel2)

# retrieve submodel1 from obj store

print(submodel1 == obj_store.get_identifiable("urn:x-test:submodel1"))

# retrieve referable element_list by Id and Id_short

print(element_list == obj_store.get_referable(identifier="urn:x-test:submodel1", id_short='ExampleSubmodelList'))

# retrieve children of element_list by id_short

print(list_element in obj_store.get_children_referable('urn:x-test:submodel1', 'ExampleSubmodelList'))
print(another_list_element in obj_store.get_children_referable('urn:x-test:submodel1',
                                                               'ExampleSubmodelList'))

# Retrieve parent of list_element by id_short

print(element_list == obj_store.get_parent_referable("list_1"))

print(aas.__dict__)
print(type(submodel1), type(aas))
