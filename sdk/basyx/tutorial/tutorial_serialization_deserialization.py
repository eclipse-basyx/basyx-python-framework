#!/usr/bin/env python3
# This work is licensed under a Creative Commons CCZero 1.0 Universal License.
# See http://creativecommons.org/publicdomain/zero/1.0/ for more information.
"""
Tutorial for the serialization and deserialization of Asset Administration Shells, Submodels and Assets into/from JSON
and XML files.
"""

import json

import aas_core3.types as aas_types
import aas_core3.xmlization as xmlizaztion
import aas_core3.jsonization as jsonization

# 'Details of the Asset Administration Shell' specifies multiple official serialization formats for AAS data. In this
# tutorial, we show how the Eclipse BaSyx Python library can be used to serialize AAS objects into JSON or XML and to
# create JSON/XML files, according to the standardized format. It is also demonstrated how these files can be parsed to
# restore the AAS objects as Python objects.
#
# Step-by-Step Guide:
# Step 1: creating Submodel and Asset Administration Shell objects
# Step 2: serializing single objects to JSON
# Step 3: parsing single objects or custom data structures from JSON
# Step 4: writing multiple identifiable objects to a (standard-compliant) JSON/XML file
# Step 5: reading the serialized aas objects from JSON/XML files


####################################################################
# Step 1: Creating Submodel and Asset Administration Shell Objects #
####################################################################

# For more details, take a look at `tutorial_create_simple_aas.py`

submodel = aas_types.Submodel(
    id='https://acplt.org/Simple_Submodel',
    submodel_elements=[
        aas_types.Property(
            id_short='ExampleProperty',
            value_type=aas_types.DataTypeDefXSD.STRING,
            value='exampleValue',
            semantic_id=aas_types.Reference(
                type=aas_types.ReferenceTypes.MODEL_REFERENCE,
                keys=[aas_types.Key(
                    type=aas_types.KeyTypes.GLOBAL_REFERENCE,
                    value='http://acplt.org/Properties/SimpleProperty'
                )]
            )
        )
    ]
)

aashell = aas_types.AssetAdministrationShell(
    id='https://acplt.org/Simple_AAS',
    asset_information=aas_types.AssetInformation(asset_kind=aas_types.AssetKind.INSTANCE, global_asset_id="test"),
    submodels=[aas_types.Reference(
        type=aas_types.ReferenceTypes.MODEL_REFERENCE,
        keys=[aas_types.Key(
            type=aas_types.KeyTypes.SUBMODEL,
            value=submodel.id
        )]
    )]
)


#######################################
# Step 2: Serializing Objects to JSON #
#######################################

shell_jsonable = jsonization.to_jsonable(aashell)
shell_string = json.dumps(shell_jsonable, indent=4)

submodel_jsonable = jsonization.to_jsonable(submodel)
submodel_string = json.dumps(submodel_jsonable, indent=4)


######################################################################
# Step 3: Parsing Single Objects or Custom Data Structures from JSON #
######################################################################

shell_jsonable_from_string = json.loads(shell_string)
shell_from_jsonable = jsonization.asset_administration_shell_from_jsonable(shell_jsonable_from_string)

submodel_jsonable_from_jsonable = json.loads(submodel_string)
submodel_from_jsonable = jsonization.submodel_from_jsonable(submodel_jsonable_from_jsonable)


######################################
# Step 4: Serializing Objects to XML #
######################################

aashell_xml = xmlizaztion.to_str(aashell)
submodel_xml = xmlizaztion.to_str(submodel)


####################################
# Step 5: Parsing Objects from XML #
####################################

aashell_from_xml = xmlizaztion.submodel_from_str(aashell_xml)
submodel_from_xml = xmlizaztion.submodel_from_str(submodel_xml)
