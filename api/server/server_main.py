import uvicorn
from fastapi import FastAPI

from server.routes import submodel, aas, aasx_file_server, aas_registry_server, submodel_registry_server
from basyx import object_store

app = FastAPI()
prefix = "" # FIXME: AAS test engines seems to enforce no prefix of any kind
# Having something like api/v.XXX might be very useful in real world scenarios when hosting multiple versions. Maybe the
# prefix might also become configurable / a start-up parameter

central_object_store = object_store.ObjectStore()

aas_router = aas.AasRouter(central_object_store)
submodel_router = submodel.SubmodelRouter(central_object_store)
aasx_file_router = aasx_file_server.AasxFileServerRouter(central_object_store)
aas_registry_router = aas_registry_server.AasRegistryRouter(central_object_store)
submodel_registry_router = submodel_registry_server.SubmodelRegistryRouter(central_object_store)

# Register router
# TODO: This can be done dynamically based on startup params
app.include_router(submodel_router.router, prefix=prefix + "/submodels")
app.include_router(aasx_file_router.router, prefix=prefix + "/aasx")
app.include_router(aas_registry_router.router, prefix=prefix + "/registry")
app.include_router(submodel_registry_router.router, prefix=prefix + "/submodels")
app.include_router(aas_router.router, prefix=prefix + "/shells")

# Start the server if this file is executed directly
if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
