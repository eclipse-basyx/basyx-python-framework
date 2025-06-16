# Server Development Status

> [!warning]
> This README tracks the development progress of the server's endpoints. Endpoints are sorted based on the
> specification's services (Submodel, AASX File Server, ...).

- **Implemented (✅)**: Currently available, but **not necessarily fully functional**.
- **Planned (📅)**: Scheduled for future implementation.
- **Not Planned (❌)**: Currently not scheduled for implementation.

> [!warning]
> The project is WIP and endpoints might be declared as 'Implemented' whilst still having issues.

> Operation Parameters (e.g. level, content, extent) are generally not supported at the moment.


Below is the status table for the endpoints, organized as specified. Content parameters (/$reference, /$metadata, etc.) 
will be implemented as separate routes, but are not listed in this table as it's a simple suffix and does only affect
serialization settings.

## AAS Service
| Endpoint                                                   | Operation | Description                                                             | Status |
|------------------------------------------------------------|-----------|-------------------------------------------------------------------------|--------|
| `/aas/shells`                                              | GET       | Returns all Asset Administration Shells                                 | ✅      |
| `/aas/shells`                                              | POST      | Creates a new Asset Administration Shell                                | ✅      |
| `/aas/shells/{aas_identifier}`                             | GET       | Returns an Asset Administration Shell by ID                             | ✅      |
| `/aas/shells/{aas_identifier}`                             | PUT       | Updates an existing Asset Administration Shell                          | ✅      |
| `/aas/shells/{aas_identifier}`                             | DELETE    | Deletes an Asset Administration Shell                                   | ✅      |
| `/aas/shells/{aas_identifier}/asset-information`           | GET       | Returns the Asset Information of a specific Asset Administration Shell  | ✅      |
| `/aas/shells/{aas_identifier}/asset-information`           | PUT       | Replaces the Asset Information of a specific Asset Administration Shell | ✅      |
| `/aas/shells/{aas_identifier}/asset-information/thumbnail` | GET       | Returns the thumbnail file of the Asset Information                     | ✅      |
| `/aas/shells/{aas_identifier}/asset-information/thumbnail` | PUT       | Replaces the thumbnail file of the Asset Information                    | ✅      |
| `/aas/shells/{aas_identifier}/asset-information/thumbnail` | DELETE    | Deletes the thumbnail file of the Asset Information                     | ✅      |


## Submodel Service
| Endpoint                                                                             | Operation | Description                                                              | Status |
|--------------------------------------------------------------------------------------|-----------|--------------------------------------------------------------------------|--------|
| `/submodels`                                                                         | GET       | Retrieve all submodels                                                   | ✅      |
| `/submodels`                                                                         | POST      | Create a new submodel                                                    | ✅      |
| `/submodels/{submodel_id}`                                                           | GET       | Retrieve a submodel by ID                                                | ✅      |
| `/submodels/{submodel_id}`                                                           | PUT       | Replace a submodel by ID                                                 | ✅      |
| `/submodels/{submodel_id}`                                                           | PATCH     | Update a submodel by ID                                                  | 📅     |
| `/submodels/{submodel_id}`                                                           | DELETE    | Delete a submodel by ID                                                  | ✅      |
| `/submodels/{submodel_id}/submodel-elements`                                         | GET       | Retrieve all elements of a specific submodel                             | ✅      |
| `/submodels/{submodel_id}/submodel-elements`                                         | POST      | Create new elements in a specific submodel                               | 📅     |
| `/submodels/{submodel_id}/submodel-elements/{id_shorts}`                             | GET       | Retrieve specific elements by short ID in a submodel                     | ✅      |
| `/submodels/{submodel_id}/submodel-elements/{id_shorts}`                             | POST      | Create specific elements by short ID in a submodel                       | ✅      |
| `/submodels/{submodel_id}/submodel-elements/{id_shorts}`                             | PUT       | Update specific elements by short ID in a submodel                       | ✅      |
| `/submodels/{submodel_id}/submodel-elements/{id_shorts}`                             | DELETE    | Delete specific elements by short ID in a submodel                       | ✅      |
| `/submodels/{submodel_id}/submodel-elements/{id_shorts}`                             | PATCH     | Partially update specific elements by short ID in a submodel             | ❌      |
| `/submodels/{submodel_id}/submodel-elements/{id_shorts}/attachment`                  | GET       | Retrieve attachments of specific elements by short ID                    | 📅     |
| `/submodels/{submodel_id}/submodel-elements/{id_shorts}/attachment`                  | PUT       | Update attachments of specific elements by short ID                      | 📅     |
| `/submodels/{submodel_id}/submodel-elements/{id_shorts}/attachment`                  | DELETE    | Delete attachments of specific elements by short ID                      | 📅     |
| `/submodels/{submodel_id}/submodel-elements/{id_shorts}/invoke`                      | POST      | Invoke operations on specific elements by short ID                       | ❌      |
| `/submodels/{submodel_id}/submodel-elements/{id_shorts}/invoke-async`                | POST      | Asynchronously invoke operations on specific elements by short ID        | ❌      |
| `/submodels/{submodel_id}/submodel-elements/{id_shorts}/qualifiers`                  | GET       | Retrieve qualifiers for specific elements by short ID                    | 📅     |
| `/submodels/{submodel_id}/submodel-elements/{id_shorts}/qualifiers`                  | POST      | Add qualifiers to specific elements by short ID                          | 📅     |
| `/submodels/{submodel_id}/submodel-elements/{id_shorts}/qualifiers/{qualifier_type}` | GET       | Retrieve qualifiers of a specific type for specific elements by short ID | 📅     |
| `/submodels/{submodel_id}/submodel-elements/{id_shorts}/qualifiers/{qualifier_type}` | PUT       | Update qualifiers of a specific type for specific elements by short ID   | 📅     |
| `/submodels/{submodel_id}/submodel-elements/{id_shorts}/qualifiers/{qualifier_type}` | DELETE    | Delete qualifiers of a specific type for specific elements by short ID   | 📅     |

## AASX File Server Interface and Operations
| Endpoint                  | Operation | Description                                        | Status |
|---------------------------|-----------|----------------------------------------------------|--------|
| `/aasx`                   | GET       | Returns all available AASX packages at the server. | ✅      |
| `/aasx/{aasx_package_id}` | GET       | Returns a specific AASX package from the server.   | ✅      |
| `/aasx`                   | POST      | Creates an AASX package at the server.             | ✅      |
| `/aasx`                   | PUT       | Replaces the AASX package at the server.           | ✅      |
| `/aasx/{aasx_package_id}` | DELETE    | Deletes a specific AASX package at the server.     | ✅      |

## AAS Registry Service
| Endpoint                             | Operation | Description                                        | Status |
|--------------------------------------|-----------|----------------------------------------------------|--------|
| `/registry/aas-descriptors`          | GET       | Returns all Asset Administration Shell Descriptors | ✅      |
| `/registry/aas-descriptors/{aas_id}` | GET       | Returns an AAS Descriptor by ID                    | ✅      |
| `/registry/aas-descriptors`          | POST      | Creates an AAS Descriptor                          | ✅      |
| `/registry/aas-descriptors/{aas_id}` | PUT       | Updates an AAS Descriptor                          | ✅      |
| `/registry/aas-descriptors/{aas_id}` | DELETE    | Deletes an AAS Descriptor                          | ✅      |

## Submodel Registry Service
| Endpoint                                       | Operation | Description                         | Status |
|------------------------------------------------|-----------|-------------------------------------|--------|
| `/registry/submodel-descriptors`               | GET       | Returns all Submodel Descriptors    | ✅      |
| `/registry/submodel-descriptors/{submodel_id}` | GET       | Returns a Submodel Descriptor by ID | ✅      |
| `/registry/submodel-descriptors`               | POST      | Creates a Submodel Descriptor       | ✅      |
| `/registry/submodel-descriptors/{submodel_id}` | PUT       | Updates a Submodel Descriptor       | ✅      |
| `/registry/submodel-descriptors/{submodel_id}` | DELETE    | Deletes a Submodel Descriptor       | ✅      |

## Discovery Service
| Endpoint                          | Operation | Description                          | Status |
|-----------------------------------|-----------|--------------------------------------|--------|
| `/discovery/aas-ids`              | GET       | Returns all AAS IDs by an Asset Link | 📅     |
| `/discovery/asset-links/{aas_id}` | GET       | Returns all Asset Links by an AAS ID | 📅     |
| `/discovery/asset-links/{aas_id}` | POST      | Posts new Asset Links                | 📅     |
| `/discovery/asset-links/{aas_id}` | DELETE    | Deletes Asset Links                  | 📅     |

## AAS Repository Service
| Endpoint                                   | Operation | Description                                 | Status |
|--------------------------------------------|-----------|---------------------------------------------|--------|
| `/shells`                                  | GET       | Returns all Asset Administration Shells     | 📅     |
| `/shells/{aas_id}`                         | GET       | Returns an Asset Administration Shell by ID | 📅     |
| `/shells/{aas_id}`                         | PUT       | Updates an Asset Administration Shell by ID | 📅     |
| `/shells/{aas_id}`                         | DELETE    | Deletes an Asset Administration Shell by ID | 📅     |
| `/shells/{aas_id}/asset-information`       | GET       | Returns Asset Information for an AAS        | 📅     |
| `/shells/{aas_id}/submodels`               | GET       | Returns all Submodels for an AAS            | 📅     |
| `/shells/{aas_id}/submodels/{submodel_id}` | GET       | Returns a Submodel by ID for an AAS         | 📅     |

## Submodel Repository Service
| Endpoint                   | Operation | Description              | Status |
|----------------------------|-----------|--------------------------|--------|
| `/submodels`               | GET       | Returns all Submodels    | 📅     |
| `/submodels/{submodel_id}` | GET       | Returns a Submodel by ID | 📅     |
| `/submodels/{submodel_id}` | PUT       | Updates a Submodel by ID | 📅     |
| `/submodels/{submodel_id}` | DELETE    | Deletes a Submodel by ID | 📅     |

## ConceptDescription Repository Service
| Endpoint                             | Operation | Description                         | Status |
|--------------------------------------|-----------|-------------------------------------|--------|
| `/concept-descriptions`              | GET       | Returns all Concept Descriptions    | 📅     |
| `/concept-descriptions/{concept_id}` | GET       | Returns a Concept Description by ID | 📅     |
| `/concept-descriptions/{concept_id}` | POST      | Creates a new Concept Description   | 📅     |
| `/concept-descriptions/{concept_id}` | PUT       | Updates a Concept Description by ID | 📅     |
| `/concept-descriptions/{concept_id}` | DELETE    | Deletes a Concept Description by ID | 📅     |


## SerializationModifiers
### Level
| Value | Status |
|-------|--------|
| Deep  | ❌      |
| Core  | ❌      |
### Content
| Value     | Status |
|-----------|--------|
| Normal    | ❌      |
| Reference | ❌      |
| Value     | ❌      |
| Path      | ❌      |
### Extent
| Value            | Status |
|------------------|--------|
| WithoutBLOBValue | ❌      |
| WithBLOBValue    | ❌      |