import aas_core3.types as aas
import aas_core3.jsonization as jsonization
import requests

property = aas.Property(
    id_short="temperature",
    value_type=aas.DataTypeDefXSD.DOUBLE,
    value="22.3"
)

submodel = aas.Submodel(
    id="urn:example:submodel:test",
    id_short="TestSubmodel",
    submodel_elements=[property]
)

aas_obj = aas.AssetAdministrationShell(
    id="urn:example:aas:test",
    id_short="TestAAS",
    asset_information=aas.AssetInformation(
        asset_kind=aas.AssetKind.INSTANCE
    ),
    submodels=[aas.Reference(
        type=aas.ReferenceTypes.EXTERNAL_REFERENCE,
        keys=[aas.Key(
            type=aas.KeyTypes.SUBMODEL,
            value=submodel.id
        )]
    )]
)

submodel_json = jsonization.to_jsonable(submodel)
aas_json = jsonization.to_jsonable(aas_obj)

BASE = "http://localhost:8000/shells"

resp1 = requests.post(BASE, json=aas_json)
print(f"AAS upload: {resp1.status_code}")
