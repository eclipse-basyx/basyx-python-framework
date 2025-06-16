# Server Design Notes

> [!warning]
> This concept is heavily WIP! Features presented here might not be implemented

## General ideas
The server is implemented using `FastAPI`.
The project is divided into distinct modules (inspired 
[by the server specification](https://industrialdigitaltwin.org/en/wp-content/uploads/sites/2/2024/10/IDTA-01002-3-0-3_SpecificationAssetAdministrationShell_Part2_API.pdf#page=128)
) to enhance maintainability and readability.

### API Classes

The `api` module contains classes that define the endpoints exposed by the server. As little logic as possible is implemented here.

### Service Classes
The `services` module contains all the necessary logic to enable the actions requested by the endpoints defined in `api`.

### Shared Data
With this structure all the routers and services are standalone and do not access each other in any way. As endpoints 
need to maintain context across service specifications, we use a central `ObjectStore` instance to handle
objects present during runtime.

### server.py
The server.py contains the main class. Here we construct our `ObjectStore` instance and with that the routers.
As every router is standalone and adds onto the current set of endpoints, we can select which specifications we want to add on startup.