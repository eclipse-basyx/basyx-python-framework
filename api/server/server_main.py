import argparse
import uvicorn
from fastapi import FastAPI

from server.routes import submodel, aas, aasx_file_server, aas_registry_server, submodel_registry_server
from basyx import object_store

app = FastAPI()
prefix = "/api/v3.0"

central_object_store = object_store.ObjectStore()

aas_router = aas.AasRouter(central_object_store)
submodel_router = submodel.SubmodelRouter(central_object_store)
aasx_file_router = aasx_file_server.AasxFileServerRouter(central_object_store)
aas_registry_router = aas_registry_server.AasRegistryRouter(central_object_store)
submodel_registry_router = submodel_registry_server.SubmodelRegistryRouter(central_object_store)

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Start the AAS Server with optional components")
parser.add_argument("--enable-submodels", action="store_true", help="Enable submodels API")
parser.add_argument("--enable-aasx", action="store_true", help="Enable AASX API")
parser.add_argument("--enable-registry", action="store_true", help="Enable registry API")
parser.add_argument("--enable-submodel-registry", action="store_true", help="Enable submodel registry API")
parser.add_argument("--enable-aas", action="store_true", help="Enable AAS API")

args = parser.parse_args()
has_args = any(vars(args).values())

# Enable all by default if no arguments were passed
if has_args:
    enable_submodels = args.enable_submodels
    enable_aasx = args.enable_aasx
    enable_registry = args.enable_registry
    enable_submodel_registry = args.enable_submodel_registry
    enable_aas = args.enable_aas
else:
    enable_submodels = enable_aasx = enable_registry = enable_submodel_registry = enable_aas = True

# Conditional router registration
if enable_submodels:
    app.include_router(submodel_router.router, prefix=prefix + "/submodels")

if enable_aasx:
    app.include_router(aasx_file_router.router, prefix=prefix + "/aasx")

if enable_registry:
    app.include_router(aas_registry_router.router, prefix=prefix + "/registry")

if enable_submodel_registry:
    app.include_router(submodel_registry_router.router, prefix=prefix + "/submodels")

if enable_aas:
    app.include_router(aas_router.router, prefix=prefix + "/aas")

# Run server (if needed)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
