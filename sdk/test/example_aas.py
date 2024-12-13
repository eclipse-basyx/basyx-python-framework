from aas_core3 import types as model
from basyx.object_store import ObjectStore
import aas_core3.types as aas_types
from basyx.aasx import DictSupplementaryFileContainer
from pathlib import Path


def create_full_example() -> ObjectStore:
    """
    Creates an object store which is filled with an example :class:`~basyx.aas.model.submodel.Submodel`,
    :class:`~basyx.aas.model.concept.ConceptDescription` and :class:`~basyx.aas.model.aas.AssetAdministrationShell`
    using the functions of this module

    :return: :class:`~basyx.aas.model.provider.DictObjectStore`
    """
    Referencetype = aas_types.ReferenceTypes("ModelReference")

    key_types = aas_types.KeyTypes("Submodel")

    key = aas_types.Key(value="some-unique-global-identifier", type=key_types)

    reference = aas_types.Reference(type=Referencetype, keys=[key])

    submodel = aas_types.Submodel(
        id="some-unique-global-identifier",
        submodel_elements=[
            aas_types.Property(
                id_short="some_property",
                value_type=aas_types.DataTypeDefXSD.INT,
                value="1984",
                semantic_id=reference
            )
        ]
    )
    file_store = DictSupplementaryFileContainer()

    with open(Path(__file__).parent.parent / 'basyx' / 'tutorial' / 'data' / 'TestFile.pdf', 'rb') as f:
        actual_file_name = file_store.add_file("/aasx/suppl/MyExampleFile.pdf", f, "application/pdf")

    if submodel.submodel_elements is not None:
        submodel.submodel_elements.append(aas_types.File(id_short="documentationFile",
                                                         content_type="application/pdf",
                                                         value=actual_file_name))

    aas = aas_types.AssetAdministrationShell(id="https://acplt.org/Test_AssetAdministrationShell",
                                             asset_information=aas_types.AssetInformation(
                                                 asset_kind=aas_types.AssetKind.TYPE),
                                             submodels=[reference])
    obj_store: ObjectStore[model.Identifiable] = ObjectStore()
    obj_store.add(aas)
    obj_store.add(submodel)
    return obj_store
